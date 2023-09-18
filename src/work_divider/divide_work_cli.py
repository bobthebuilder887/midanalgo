import argparse
from collections.abc import Sequence

from work_divider.assign_workers import generate_work_sheet


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="Midan's Sheet Processor",
        description="Divide work among co-workers using Midan's scoring system",
        epilog="All files have to be of .xlsx type",
    )

    # Table file path
    parser.add_argument(
        "-t",
        "--table",
        help="Path to table file.",
        type=str,
        required=True,
    )
    # Base Table file path
    parser.add_argument(
        "-b",
        "--table-base",
        help="Path to table base file.",
        type=str,
        required=True,
    )
    # Output Table file path
    parser.add_argument(
        "-o",
        "--output-file",
        help="Path to output file.",
        type=str,
        default="output.xlsx",
        required=False,
    )

    # Parse arguments
    args = parser.parse_args(argv)

    generate_work_sheet(args.table, args.table_base, args.output_file)


if __name__ == "__main__":
    main()
