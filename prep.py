"""
Создает 50 zip-архивов, в каждом 100 xml файлов со случайными данными следующей структуры:

<root>
    <var name=’id’ value=’<случайное уникальное строковое значение>’/>
    <var name=’level’ value=’<случайное число от 1 до 100>’/>
    <objects>
        <object name=’<случайное строковое значение>’/>
        <object name=’<случайное строковое значение>’/>
        …
    </objects>
</root>

В тэге objects случайное число (от 1 до 10) вложенных тэгов object.

Usage: python prep.py archives
"""
import argparse
import uuid
from pathlib import Path
from random import randint
from shutil import make_archive, rmtree
from tempfile import TemporaryDirectory
from xml.etree import ElementTree

PROJECT_ROOT = Path(__file__).parent.resolve()

ARCHIVE_COUNT = 50
XML_COUNT = 100
OBJECTS_MAX_COUNT = 10


def random_string():
    """Generate random string"""
    return uuid.uuid4().hex[:6]


class Unique:
    """Unique values generator"""
    values = set()

    @staticmethod
    def string() -> str:
        """Generate unique string"""
        value = random_string()
        while value in Unique.values:
            value = random_string()

        Unique.values.add(value)

        return value


def create_xml(filename: Path):
    """Create XML file"""
    root = ElementTree.Element('root')

    var1 = ElementTree.SubElement(root, 'var')
    var1.set('name', 'id')
    var1.set('value', Unique.string())

    var2 = ElementTree.SubElement(root, 'var')
    var2.set('name', 'level')
    var2.set('value', str(randint(1, 100)))

    objects = ElementTree.Element('objects')

    for _ in range(randint(1, OBJECTS_MAX_COUNT)):
        obj = ElementTree.SubElement(objects, 'object')
        obj.set('name', random_string())

    root.append(objects)

    tree = ElementTree.ElementTree(root)
    tree.write(filename)


def prepare_archive_content(directory: Path):
    """Generate 100 XML files"""
    directory.mkdir(parents=True, exist_ok=True)

    for idx in range(XML_COUNT):
        filename = directory / f'{idx}.xml'
        create_xml(filename)


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='Working directory')
    args = parser.parse_args()

    output_dir = Path(args.dir)

    if output_dir.exists():
        rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(ARCHIVE_COUNT):
        with TemporaryDirectory(dir=PROJECT_ROOT) as tmpdir:
            prepare_archive_content(Path(tmpdir))
            archive_name = str(output_dir / str(idx))
            make_archive(archive_name, 'zip', tmpdir)


if __name__ == "__main__":
    main()
