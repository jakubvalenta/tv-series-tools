import listio


def migrate_custom_map_to_csv():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Migrate custom map to CSV'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='input custom map file path')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='output csv file path')
    args = parser.parse_args()

    listio.write_map(
        args.outputfile,
        [line.split(' :: ') for line in listio.read_lines(args.inputfile)]
    )

    sys.exit()
