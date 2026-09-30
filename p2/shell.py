#!/usr/bin/env python3
"""Простой интерпретатор командной строки.

Поддерживает echo, cat, wc, pwd, exit, help, переменные ($X),
одинарные и двойные кавычки, пайпы и вызов внешних программ.

Запуск: python3 shell.py
"""

import io
import os
import subprocess
import sys
from dataclasses import dataclass

# Переменные, которые пользователь задал в шелле через X=value
ENV = {}

# Встроенные команды. Все остальное запускаем как внешнюю программу
BUILTINS = ["echo", "cat", "wc", "pwd", "exit", "help"]

HELP_TEXT = """Встроенные команды:
  echo [ARG]...   вывести аргументы
  cat [FILE]      вывести содержимое файла
  wc [FILE]       количество строк, слов и байт
  pwd             текущая директория
  exit [CODE]     выйти из шелла
  help            эта справка
"""


def is_valid_var_name(name):
    """Имя переменной: буквы, цифры и _, не начинается с цифры."""
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == "_"):
        return False
    return all(ch.isalnum() or ch == "_" for ch in name)


def parse_assignment(word):
    """Разбирает X=value. Возвращает (имя, значение) или None."""
    if "=" not in word:
        return None
    name, value = word.split("=", 1)
    if is_valid_var_name(name):
        return name, value
    return None


@dataclass
class Pipeline:
    stages: list
    source: str


class Command:
    """Базовый класс для команд шелла."""

    def run(self, args):
        raise NotImplementedError

    def parse_flags(self, args):
        raise NotImplementedError

    def help(self):
        raise NotImplementedError

    def autocomplete(self, prefix):
        raise NotImplementedError


class EchoCommand(Command):
    def run(self, args):
        print(" ".join(args))

    def parse_flags(self, args):
        return {}, args

    def help(self):
        return "echo [ARG]... - вывести аргументы"

    def autocomplete(self, prefix):
        raise NotImplementedError("echo не поддерживает автодополнение")


class PwdCommand(Command):
    def run(self, args):
        print(os.getcwd())

    def parse_flags(self, args):
        return {}, []

    def help(self):
        return "pwd - текущая директория"

    def autocomplete(self, prefix):
        raise NotImplementedError("pwd не поддерживает автодополнение")


class ExitCommand(Command):
    def run(self, args):
        code = int(args[0]) if args else 0
        sys.exit(code)

    def parse_flags(self, args):
        return {}, args

    def help(self):
        return "exit [CODE] - выйти из шелла"

    def autocomplete(self, prefix):
        return []


class PluginManager:
    """Загрузка команд из плагинов. Пригодится, когда команд станет много."""

    def __init__(self):
        self.plugins = {}

    def load_plugins(self, directory):
        for name in os.listdir(directory):
            if name.endswith(".py"):
                self.plugins[name[:-3]] = os.path.join(directory, name)
        return self.plugins

    def get(self, name):
        return self.plugins.get(name)


class Shell:
    def __init__(self):
        self.commands = {
            "echo": EchoCommand(),
            "pwd": PwdCommand(),
            "exit": ExitCommand(),
        }
        self.last_code = 0

    def loop(self):
        interactive = sys.stdin.isatty()
        while True:
            if interactive:
                sys.stdout.write("$ ")
                sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:
                return self.last_code
            line = line.rstrip("\n")
            if line.strip() == "":
                continue
            self.run_line(line)

    def run_line(self, line):
        # 1. Подставляем переменные
        result = ""
        i = 0
        while i < len(line):
            if line[i] == "$":
                j = i + 1
                while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                    j += 1
                name = line[i + 1:j]
                if name == "":
                    result += "$"
                    i += 1
                    continue
                result += ENV.get(name, os.environ.get(name, ""))
                i = j
            else:
                result += line[i]
                i += 1
        line = result

        # 2. Разбиваем на слова
        tokens, quoted = self.tokenize(line)
        if not tokens:
            return

        # 3. Присваивание X=value
        if len(tokens) == 1 and not quoted[0]:
            assignment = parse_assignment(tokens[0])
            if assignment is not None:
                ENV[assignment[0]] = assignment[1]
                self.last_code = 0
                return

        # 4. Делим на команды пайплайна
        stages = [[]]
        for token, is_quoted in zip(tokens, quoted):
            if token == "|" and not is_quoted:
                stages.append([])
            else:
                stages[-1].append(token)
        pipeline = Pipeline(stages=stages, source=line)

        for stage in pipeline.stages:
            if not stage:
                print(f"syntax error near unexpected token `|' in: {pipeline.source}", file=sys.stderr)
                self.last_code = 2
                return

        # 5. Исполняем. Вывод каждой команды, кроме последней,
        # перехватываем и отдаем на вход следующей
        data = None
        for index, stage in enumerate(pipeline.stages):
            is_last = index == len(pipeline.stages) - 1
            buffer = io.StringIO()
            old_stdout = sys.stdout
            if not is_last:
                sys.stdout = buffer
            try:
                self.execute(stage[0], stage[1:], data)
            finally:
                sys.stdout = old_stdout
            data = None if is_last else buffer.getvalue()

    # ХАК: кавычки тут обрабатываются странно, но оно работает.
    # Не трогать, пока не перепишем токенизатор.
    # Старая версия ниже, в tokenize_old.
    def tokenize(self, line):
        tokens = []
        quoted = []
        current = ""
        current_quoted = False
        quote = None
        for ch in line:
            if quote:
                if ch == quote:
                    quote = None
                else:
                    current += ch
            elif ch in "'\"":
                quote = ch
                current_quoted = True
            elif ch == " ":
                if current or current_quoted:
                    tokens.append(current)
                    quoted.append(current_quoted)
                    current = ""
                    current_quoted = False
            elif ch == "|":
                if current or current_quoted:
                    tokens.append(current)
                    quoted.append(current_quoted)
                    current = ""
                    current_quoted = False
                tokens.append("|")
                quoted.append(False)
            else:
                current += ch
        if current or current_quoted:
            tokens.append(current)
            quoted.append(current_quoted)
        return tokens, quoted

    def tokenize_old(self, line):
        # старая версия, оставлена на всякий случай
        return line.split(" ")

    def execute(self, name, args, stdin_data):
        if name not in BUILTINS:
            self.run_external(name, args, stdin_data)
            return

        if name in self.commands:
            self.commands[name].run(args)
            self.last_code = 0
        elif name == "cat":
            if args:
                try:
                    with open(args[0]) as f:
                        content = f.read()
                except FileNotFoundError:
                    print("cat: " + args[0] + ": No such file or directory", file=sys.stderr)
                    self.last_code = 1
                    return
                except IsADirectoryError:
                    print("cat: " + args[0] + ": Is a directory", file=sys.stderr)
                    self.last_code = 1
                    return
            else:
                content = stdin_data or ""
            print(content, end="")
            self.last_code = 0
        elif name == "wc":
            if args:
                try:
                    with open(args[0]) as f:
                        content = f.read()
                except FileNotFoundError:
                    print("wc: cannot open file " + args[0], file=sys.stderr)
                    self.last_code = 1
                    return
                except IsADirectoryError:
                    print("wc: " + args[0] + " is a directory", file=sys.stderr)
                    self.last_code = 1
                    return
            else:
                content = stdin_data or ""
            lines = content.count("\n")
            words = len(content.split())
            size = len(content.encode())
            if args:
                print(f"{lines} {words} {size} {args[0]}")
            else:
                print(f"{lines} {words} {size}")
            self.last_code = 0
        elif name == "help":
            print(HELP_TEXT, end="")
            self.last_code = 0

    def run_external(self, name, args, stdin_data):
        try:
            result = subprocess.run(
                [name] + args,
                input=stdin_data or "",
                capture_output=True,
                text=True,
                env={**os.environ, **ENV},
            )
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
            self.last_code = result.returncode
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(Shell().loop())
