from argparse import ArgumentParser
from collections import Counter
import csv
from pathlib import Path


def summarize(path, encoding):
    with path.open(encoding=encoding, newline='') as stream:
        dialect = csv.Sniffer().sniff(stream.readline(), delimiters=',;\t')
        stream.seek(0)
        reader = csv.DictReader(stream, dialect=dialect)
        if not {'Año', 'Departamento'} <= set(reader.fieldnames or []):
            raise ValueError('Se necesitan las columnas Año y Departamento del CSV de casos.')
        years, departments = Counter(), Counter()
        total = 0
        for row in reader:
            total += 1
            year = (row['Año'] or '').strip()
            if year.isdecimal() and 1800 <= int(year) <= 2100:
                years[int(year)] += 1
            department = (row['Departamento'] or '').strip().upper() or 'SIN INFORMACIÓN'
            departments[department] += 1
    if not total:
        raise ValueError('El CSV no contiene casos.')
    return total, years, departments


def export(path, header, frequencies):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(sorted(frequencies.items()))


def main():
    parser = ArgumentParser(description='Resume los casos por año y por departamento.')
    parser.add_argument('csv', type=Path)
    parser.add_argument('--salida', required=True, type=Path)
    parser.add_argument('--encoding', default='utf-8-sig', help='Usa cp1252 si corresponde al archivo.')
    args = parser.parse_args()
    total, years, departments = summarize(args.csv, args.encoding)
    args.salida.mkdir(parents=True, exist_ok=True)
    export(args.salida / 'registros_por_anio.csv', ('anio', 'registros'), years)
    export(args.salida / 'registros_por_departamento.csv', ('departamento', 'registros'), departments)
    print(f'Registros leídos: {total:,}; sin año utilizable: {total - sum(years.values()):,}')


if __name__ == '__main__':
    main()
