from pathlib import Path

import pandas as pd
import pytest

from work_divider import assign_workers


def test_assing_names() -> None:
    mock_names = ["A", "B", "C"]
    mock_invoices = {i: [1, 2, 3] for i in range(len(mock_names))}
    named_invoices = assign_workers.assign_names(mock_invoices, mock_names)

    assert len(named_invoices) == len(mock_invoices)
    assert set(named_invoices) == set(mock_names)


def test_match_invoices() -> None:
    from work_divider import batching

    optimal_split = [[2, 3], [1, 4], [5]]

    batch_a = batching.Batch(score=5, invoice_numbers=[1, 9, 3])
    batch_b = batching.Batch(score=4, invoice_numbers=[8, 5])
    batch_c = batching.Batch(score=3, invoice_numbers=[5])
    batch_d = batching.Batch(score=2, invoice_numbers=[15, 10])
    batch_e = batching.Batch(score=1, invoice_numbers=[19, 20])

    mock_batches = {
        batch_a.id: batch_a,
        batch_b.id: batch_b,
        batch_c.id: batch_c,
        batch_d.id: batch_d,
        batch_e.id: batch_e,
    }

    # Get batched invoice numbers
    invoice_numbers: list[int] = []
    for batch in mock_batches.values():
        invoice_numbers.extend(batch.invoice_numbers)

    matching_invoices = assign_workers.match_invoices(mock_batches, optimal_split)

    # Make sure all of batches have been emptied out
    assert mock_batches == {}

    # Make sure invoice numbers are assigned per worker
    assert len(matching_invoices) == len(optimal_split)

    # Get matched invoice numbers
    matched_invoice_numbers: list[int] = []
    for invoice_split in matching_invoices.values():
        matched_invoice_numbers.extend(invoice_split)

    # Make sure all invoice numbers are assigned to workers
    assert len(invoice_numbers) == len(matched_invoice_numbers)
    assert set(invoice_numbers) == set(matched_invoice_numbers)


def test_generate_worksheet(
    table_path: Path,
    tablebase_path: Path,
    output_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    assign_workers.generate_work_sheet(table_path, tablebase_path, output_path)

    # Test if prints correct statement
    assert capsys.readouterr().out == f"File saved to {output_path}\n"

    # Test if generates file
    assert Path(output_path).exists()

    output = pd.read_excel(output_path)

    # Make sure there is a Worker column and every worker name is assigned
    assert output["Worker"].dropna().unique().shape[0] == 11
