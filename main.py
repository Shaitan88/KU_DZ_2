import xml.etree.ElementTree as ET
import os
import re
import subprocess

def analyze_dependencies(package_name, source_dir):
    """
    анализирует зависимости Java-пакета, извлекая информацию из import statements
    package_name - имя анализируемого пакета
    source_dir - путь к директории с исходным кодом Java
    Returns - Словарь, где ключи - имена пакетов, а значения - списки зависимостей
    """

    source_parts = source_dir.replace("./", "").split("/")  # разбиваем source_dir на части пути
    package_path_parts = package_name.replace(".", "/").split("/") # разбиваем package_name на части пути
    package_path = "/".join(package_path_parts[len(source_parts):]) # относительный путь к пакету внутри source_dir
    dependencies = {} # Словарь для хранения зависимостей

    for root, _, files in os.walk(source_dir): # рекурсивно обходим все директории и файлы
        for file in files:
            if file.endswith(".java"): # обрабатываем только Java-файлы
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    relative_path = os.path.relpath(root, source_dir).replace("\\", "/") # относительный путь текущей директории
                    if package_path == relative_path: # проверяем, принадлежит ли файл анализируемому пакету
                        if package_name not in dependencies:
                            dependencies[package_name] = []
                        for line in f: # читаем файл построчно
                            match = re.search(r"import\s+(.*);", line) # ищем import statements
                            if match:
                                dependency = match.group(1) # извлекаем имя зависимости
                                dependencies[package_name].append(dependency) # добавляем зависимость в словарь

    # Отладка
    print(f"Текущая директория: {root}")
    print(f"Относительный путь: {relative_path}")
    print(f"package_path: {package_path}")
    print(f"dependencies: {dependencies}")

    return dependencies


def generate_dot(dependencies, output_path):
    """
    генерирует DOT-файл, представляющий граф зависимостей
    dependencies: Словарь зависимостей (результат analyze_dependencies)
    output_path: Путь к выходному DOT-файлу
    """
    with open(output_path, 'w') as f:
        f.write("digraph dependencies {\n") # начало DOT-файла
        for package, deps in dependencies.items(): # перебираем пакеты и их зависимости
            for dep in deps:
                f.write(f'  "{package}" -> "{dep}";\n') # записываем зависимость в формате DOT
        f.write("}\n") # конец DOT-файла


def main():
    try:
        tree = ET.parse("./config.xml") # парсим config.xml
        root = tree.getroot()
        graphviz_path = root.find("graphvizPath").text # путь к dot.exe
        package_name = root.find("packageName").text # имя пакета
        output_path = root.find("outputPath").text # путь к выходному DOT-файлу
        source_dir = root.find("sourceDir").text # путь к исходникам

        dependencies = analyze_dependencies(package_name, source_dir)
        generate_dot(dependencies, output_path)

        subprocess.run([graphviz_path, "-Tpng", output_path, "-o", "./dependencies.png"], check=True)  # генерируем PNG с зависимостями

        print(f"DOT-файл успешно создан: {output_path}")

    except FileNotFoundError:
        print("Ошибка: config.xml не найден.")
    except AttributeError:
        print("Ошибка: некорректный формат config.xml.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении Graphviz: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()