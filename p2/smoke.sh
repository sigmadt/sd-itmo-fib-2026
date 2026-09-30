#!/usr/bin/env bash
# Быстрая проверка шелла: подаем команды на вход и сравниваем вывод с ожидаемым.
#   ./smoke.sh              проверить монолит shell.py
#   ./smoke.sh refactored   проверить версию из папки refactored/

cd "$(dirname "$0")" || exit 1

case "${1:-monolith}" in
  monolith)   RUN=(python3 shell.py) ;;
  refactored) RUN=(python3 refactored/shell.py) ;;
  *) echo "использование: ./smoke.sh [refactored]"; exit 1 ;;
esac

pass=0
fail=0

check() {
  local name="$1" input="$2" expected="$3" actual
  actual=$(printf '%s\n' "$input" | "${RUN[@]}" 2>/dev/null)
  if [ "$actual" == "$expected" ]; then
    echo "ok    $name"
    pass=$((pass + 1))
  else
    echo "FAIL  $name"
    echo "      ожидали:  $(printf '%q' "$expected")"
    echo "      получили: $(printf '%q' "$actual")"
    fail=$((fail + 1))
  fi
}

check "echo"               "echo hello world"            "hello world"
check "переменные"         $'X=42\necho $X'              "42"
check "двойные кавычки"    'echo "a  b"'                 "a  b"
check "cat"                "cat data.txt"                "$(cat data.txt)"
check "wc"                 "wc data.txt"                 "3 9 45 data.txt"
check "пайп echo | wc"     "echo hello | wc"             "1 1 6"
check "пайп cat | wc"      "cat data.txt | wc"           "3 9 45"
check "pwd"                "pwd"                         "$(pwd -P)"
check "внешняя программа"  "echo abc | tr a-z A-Z"       "ABC"
check "exit"               $'echo before\nexit\necho after'  "before"

echo
echo "прошло: $pass, упало: $fail"
[ "$fail" -eq 0 ]
