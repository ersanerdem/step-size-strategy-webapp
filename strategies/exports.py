"""Excel export (in memory). Replaces ``xlwt`` (unmaintained, legacy .xls only)."""

from __future__ import annotations

import io
from typing import Sequence

from openpyxl import Workbook


def rows_to_xlsx(rows: Sequence[dict], columns: Sequence[tuple[str, str, str]]) -> bytes:
    """``columns`` is a sequence of ``(key, plain_header, latex_header)`` tuples."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Euler Method"
    sheet.append([header for _key, header, _latex in columns])  # numbers stay numbers
    for row in rows:
        sheet.append([row[key] for key, _header, _latex in columns])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
