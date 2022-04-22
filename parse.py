"""
Обрабатывает директорию с полученными zip архивами, разбирает вложенные xml файлы и формирует 2 csv файла:
Первый:
    id, level - по одной строке на каждый xml файл
Второй:
    id, object_name - по отдельной строке для каждого тэга object (получится от 1 до 10 строк на каждый xml файл)

Usage: python parse.py archives
"""
import argparse
import csv
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).parent.resolve()


def get_zip_files(directory: Path):
    """Get ZIP files in the directory"""
    for archive in directory.glob('*.zip'):
        yield archive


def parse_xml(content: str) -> tuple[str, int, list[str]]:
    """Parse XML file"""
    root = ElementTree.fromstring(content)
    level = int(root.find('.//var[@name="level"]').attrib['value'])
    record_id = root.find('.//var[@name="id"]').attrib['value']
    objects = []
    for node in root.findall('.//object'):
        objects.append(node.attrib['name'])
    return record_id, level, objects


def get_xml_content(directory) -> Iterable[str]:
    """Iterate over XML files content in archive"""
    for zip_file in get_zip_files(directory):
        with ZipFile(zip_file) as archive:
            for file in archive.filelist:
                yield archive.read(file.filename)


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='Working directory')
    args = parser.parse_args()

    levels = []
    objects = []

    with Pool() as pool:
        for result in pool.imap_unordered(parse_xml, get_xml_content(Path(args.dir))):
            record_id, level, objs = result
            levels.append((record_id, level))
            for obj in objs:
                objects.append((record_id, obj))

    with (PROJECT_ROOT / 'levels.csv').open('w', newline='') as levels_file:
        levels_writer = csv.writer(levels_file)
        levels_writer.writerows(levels)

    with (PROJECT_ROOT / 'objects.csv').open('w', newline='') as objects_file:
        objects_writer = csv.writer(objects_file)
        objects_writer.writerows(objects)


if __name__ == '__main__':
    main()
