<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_read.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_read.c

Purpose: Implements `wt read`, a simple command-line lookup tool for reading string values by record-number or string keys from a table.

Important APIs/functions: `usage` defines `read uri key ...`. `util_read` resolves the first operand as a table URI, opens a cursor, validates key format is `r` or `S` and value format is `S`, sets keys from command arguments, calls `cursor->search`, retrieves values with `cursor->get_value`, and prints each value.

Control flow: After option parsing, it requires at least a URI and one key. It frees the resolved URI immediately after `open_cursor`. Record-number keys are parsed through `util_str2num`; string keys are passed directly. Missing keys are reported with `util_err(..., 0, "%s: not found")` and remembered so the final exit status is nonzero even if later keys succeed.

State and persistence behavior: Read-only from the database perspective. It opens a session cursor and uses cursor state for each search; it does not close the cursor explicitly in this file, relying on utility/session cleanup at process teardown or higher-level lifecycle.

Dependencies and integration points: Depends on WiredTiger cursor API, `util_uri`, `util_str2num`, `util_cerr`, `WT_STREQ`, and command globals. It integrates with tables that have simple scalar key/value formats and intentionally excludes compound or binary formats.

Risks: Unsupported formats return after opening the cursor without explicit cursor close. Printed string values are emitted raw, so embedded terminal control characters or newlines can affect output consumers. A single invalid record number aborts the command immediately.

Test signals: Useful tests cover string-key reads, record-number reads, `WT_NOTFOUND` exit status, unsupported key/value formats, invalid numeric record keys, and stdout write failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_read.c -->
