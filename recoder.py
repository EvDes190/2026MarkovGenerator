#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def convert_to_windows1251(input_file, output_file=None, encoding_in='utf-8'):
    """
    Конвертирует текстовый файл в кодировку windows-1251

    Args:
        input_file (str): путь к входному файлу
        output_file (str): путь к выходному файлу (если None, будет создан с суффиксом _1251)
        encoding_in (str): исходная кодировка файла (по умолчанию utf-8)

    Returns:
        bool: True если конвертация успешна, False в противном случае
    """
    try:
        # Проверяем существование входного файла
        if not os.path.exists(input_file):
            print(f"Ошибка: Файл {input_file} не найден")
            return False

        # Определяем выходной файл
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.parent / f"{input_path.stem}_1251{input_path.suffix}")

        # Читаем содержимое файла в исходной кодировке
        print(f"Чтение файла {input_file} в кодировке {encoding_in}...")
        with open(input_file, 'r', encoding=encoding_in) as f:
            content = f.read()

        # Записываем в windows-1251
        print(f"Запись файла {output_file} в кодировке windows-1251...")
        with open(output_file, 'w', encoding='windows-1251') as f:
            f.write(content)

        print(f"✓ Конвертация завершена успешно!")
        print(f"  Исходный файл: {input_file}")
        print(f"  Выходной файл: {output_file}")
        return True

    except UnicodeDecodeError:
        print(f"Ошибка: Не удалось прочитать файл в кодировке {encoding_in}")
        print("Попробуйте указать другую исходную кодировку")
        return False
    except UnicodeEncodeError:
        print("Ошибка: Некоторые символы не могут быть преобразованы в windows-1251")
        print("Возможно, в файле есть символы, отсутствующие в этой кодировке")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def print_usage():
    """Выводит инструкцию по использованию"""
    print("=" * 60)
    print("КОНВЕРТЕР ТЕКСТОВЫХ ФАЙЛОВ В WINDOWS-1251")
    print("=" * 60)
    print("\nИспользование:")
    print("  python script.py <путь_к_файлу> [опции]")
    print("\nОпции:")
    print("  -o, --output <файл>    : имя выходного файла")
    print("  -e, --encoding <код>    : исходная кодировка (по умолчанию utf-8)")
    print("\nПримеры:")
    print("  python script.py document.txt")
    print("  python script.py document.txt -o result.txt")
    print("  python script.py document.txt -e cp866")
    print("  python script.py document.txt --encoding windows-1251")
    print("=" * 60)

def main():
    # Проверяем, есть ли аргументы командной строки
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # Парсим аргументы вручную
    input_file = None
    output_file = None
    encoding = 'utf-8'

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print("Ошибка: Не указано имя выходного файла после опции", arg)
                sys.exit(1)
        elif arg in ['-e', '--encoding']:
            if i + 1 < len(sys.argv):
                encoding = sys.argv[i + 1]
                i += 2
            else:
                print("Ошибка: Не указана кодировка после опции", arg)
                sys.exit(1)
        elif arg in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        else:
            # Предполагаем, что это путь к входному файлу
            if input_file is None:
                input_file = arg
                i += 1
            else:
                print(f"Ошибка: Неизвестный аргумент {arg}")
                print_usage()
                sys.exit(1)

    # Проверяем, что входной файл указан
    if input_file is None:
        print("Ошибка: Не указан входной файл")
        print_usage()
        sys.exit(1)

    # Выполняем конвертацию
    success = convert_to_windows1251(input_file, output_file, encoding)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()