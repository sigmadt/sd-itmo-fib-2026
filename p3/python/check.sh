#!/usr/bin/env bash
# Проверка, что рефакторинг не поменял поведение:
# запускаем сценарий и сравниваем вывод с эталоном.
#   ./check.sh
cd "$(dirname "$0")" || exit 1
if diff <(python3 main.py 2>&1) expected_output.txt; then
  echo "OK: вывод совпадает с эталоном"
else
  echo "ОТЛИЧИЕ: строки с < это ваш вывод, с > это эталон"
  exit 1
fi
