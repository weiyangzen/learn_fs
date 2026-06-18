<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_write.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_write.c

Purpose: Implements `wt write`, a simple table mutation command for inserting/appending string values and removing one key.

Important APIs/functions: `usage` defines `write [-aor] uri key value ...`. `util_write` parses append, overwrite, and remove flags; validates operand shape; resolves the table URI; opens a cursor with `append=<bool>,overwrite=<bool>`; validates key format `r` or `S` and value format `S`; then performs `cursor->insert` or `cursor->remove`.

Control flow: Append mode treats operands after URI as values and lets WiredTiger assign record numbers. Remove mode requires exactly one key and stops after one `cursor->remove`. Normal mode consumes key/value pairs. Record-number keys use `util_str2num`; string keys are direct.

State and persistence behavior: Mutates persistent table data through cursor insert/remove operations. Overwrite behavior is controlled by cursor config; append mode depends on record-number tables. No explicit transaction boundaries are created in this file, so command behavior follows the session/connection defaults established by the utility main path.

Dependencies and integration points: Depends on WiredTiger cursor API, utility URI and numeric helpers, `__wt_snprintf`, and cursor format strings. It is the write-side counterpart to `util_read` for simple table layouts.

Risks: `-a` and `-r` are not rejected together at option parse time; append takes precedence in operand validation, while remove still causes `cursor->remove` without setting an append-assigned key, which is an invalid/confusing combination. Unsupported formats return without explicit cursor close. Raw string values cannot express arbitrary binary formats.

Test signals: Tests should cover insert, overwrite false/true, append on record-number tables, remove, invalid option combinations, unsupported formats, invalid record keys, and persistence observed by a later read.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_write.c -->
