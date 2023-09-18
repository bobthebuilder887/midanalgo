import os
from pathlib import Path

from work_divider import assign_workers


def test_main(table_path: Path, tablebase_path: Path, capsys) -> None:
    output_path = "tests/output.xlsx"

    assign_workers.main(
        argv=["-t", str(table_path), "-b", str(tablebase_path), "-o", output_path],
    )

    # Test if prints correct statement
    assert capsys.readouterr().out == f"File saved to {output_path}\n"

    # Test if generates file
    assert Path(output_path).exists()

    os.remove(output_path)
