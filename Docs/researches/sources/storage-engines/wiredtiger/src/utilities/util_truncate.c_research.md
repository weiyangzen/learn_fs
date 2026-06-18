<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_truncate.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_truncate.c

Purpose: Implements `wt truncate`, removing all data from a table URI.

Important APIs/functions: `usage` defines `truncate uri`. `util_truncate` resolves the sole operand as a table URI and calls `session->truncate(session, uri, NULL, NULL, NULL)`.

Control flow: It supports only `-?`, requires exactly one operand, frees the resolved URI after the truncate call, and reports errors with `util_err`.

State and persistence behavior: Mutates persistent table contents by truncating the full object range. Passing `NULL` cursors and config requests a whole-object truncate through WiredTiger.

Dependencies and integration points: Public `WT_SESSION::truncate`, `util_uri`, `util_usage`, and `util_err`. This command is a destructive administrative shortcut in the `wt` utility.

Risks: There is no confirmation prompt or dry-run path. URI resolution defaults to table, so accidental table name entry can erase all records. Recovery semantics depend on WiredTiger transaction/log configuration outside this file.

Test signals: Tests should cover operand validation, URI resolution, successful full truncate, error propagation, and verification that data is gone after the command in an integration database.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_truncate.c -->
