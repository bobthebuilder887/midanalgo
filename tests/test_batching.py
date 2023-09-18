import random

import pandas as pd
import pytest

from work_divider import batching


@pytest.fixture(scope="module")
def table() -> pd.DataFrame:
    from work_divider import sheets

    return sheets.read_table("tests/sample_data.xlsx")


@pytest.fixture(scope="module")
def tablebase() -> pd.DataFrame:
    from work_divider import sheets

    return sheets.read_tablebase("tests/sample_tablebase.xlsx")


def test_batch() -> None:
    batch_a = batching.Batch()
    batch_b = batching.Batch()

    # Make sure every batch has a unique id
    assert batch_a.id != batch_b.id

    # Make sure invoices are added correctly
    batch_a.add_invoice(1, 1)

    assert batch_a.invoice_numbers == [1]
    assert batch_a.score == 1


def test_gen_batches(
    table: pd.DataFrame,
    tablebase: pd.DataFrame,
) -> None:
    # Process table for batching
    processed_table = batching.process_table(table, tablebase)
    assert "score" in processed_table.columns

    # Generate batches
    batches = batching.gen_batches(processed_table)

    # Make sure every batch has a unique id
    assert len(batches) == len(set(batches))

    # Make sure no invoice is scored 0
    assert all(batch.score > 0 for batch in batches.values())

    # Get batch scores
    scores = batching.get_scores(batches)

    # Make sure every batch has a matching score
    assert len(batches) == len(scores)

    # Match invoices with scores (Happy case)
    random_score = random.choice(scores)
    batches, invoices = batching.find_matching_invoices(random_score, batches)

    # Make sure the function deletes used batch
    assert len(batches) == len(scores) - 1
    # Make sure the invoice has items
    assert len(invoices) > 0

    # Match invoices with scores (Bad case)
    with pytest.raises(ValueError):
        batching.find_matching_invoices(-1, batches)
