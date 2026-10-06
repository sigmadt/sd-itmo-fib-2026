#!/usr/bin/env bash
# Проверка, что рефакторинг не поменял поведение:
# компилируем, запускаем сценарий и сравниваем вывод с эталоном.
#   ./check.sh
cd "$(dirname "$0")" || exit 1
# Классы собираем во временную папку .build и удаляем ее после проверки
rm -rf .build
trap 'rm -rf .build' EXIT
if ! javac -encoding UTF-8 -d .build $(find src -name '*.java'); then
  echo "ОШИБКА КОМПИЛЯЦИИ: исправьте ошибки выше и запустите проверку снова"
  exit 1
fi
# Явно задаем UTF-8 и перевод строки \n, чтобы вывод не зависел от ОС
if diff <(java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dline.separator=$'\n' -cp .build Main 2>&1) expected_output.txt; then
  echo "OK: вывод совпадает с эталоном"
else
  echo "ОТЛИЧИЕ: строки с < это ваш вывод, с > это эталон"
  exit 1
fi
