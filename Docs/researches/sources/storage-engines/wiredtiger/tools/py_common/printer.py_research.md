# sources/storage-engines/wiredtiger/tools/py_common/printer.py

Purpose: centralizes formatted decode output for binary page tooling, including split raw-byte annotations, cell numbering, packed integer/string heuristics, and binary hex dumps.

Important APIs and control flow: `Printer.begin_cell()` records a cell prefix and resets saved bytes; `end_cell()` clears cell state; `rint()` prints saved input bytes alongside decoded text when split mode is enabled, then prints the requested line with cell indentation. `raw_bytes()` tries to describe byte strings as packed integers followed by UTF-8 text, falling back to `binary_to_pretty_string()`. `binary_to_pretty_string()` renders bytes as hex plus printable ASCII columns. `dumpraw_to_log()` preserves the input file position, reads 256 bytes around a position, and logs a formatted dump.

State and persistence behavior: `Printer` holds transient output formatting state (`cellpfx`, `in_cell`) and reads saved-byte state from its `BinaryFile`. It writes to stdout and logger only.

Dependencies and integration points: used by `file_format`, `disagg`, and `btree_format` page/cell printing. It depends on `binary_data.unpack_int()` and `binary_data.BinaryFile.saved_bytes()`.

Risks: `raw_bytes()` uses heuristics, so packed integers and strings can be misclassified; `btree_format` already notes a FIXME around this behavior. `rint()` prints directly rather than using a provided stream, which limits reuse and test capture options. Bare `except` in string decoding hides the specific decode failure.

Test signals: there are no direct unit tests in this subset. Indirect coverage comes from decode tests that assert output content or parse pages after printing.
