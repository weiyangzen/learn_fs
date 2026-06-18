<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_printlog.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_printlog.c

Purpose: Implements `wt printlog`, formatting WiredTiger log records with optional output file, LSN range, message-only filtering, redaction override, and hexadecimal item display.

Important APIs/functions: `usage` describes `-f`, `-l`, `-m`, `-u`, and `-x`. `util_printlog` parses flags, decodes `-l` as either `start-file,start-offset` or `start-file,start-offset,end-file,end-offset` with `sscanf`, builds `WT_LSN` values using `WT_SET_LSN`, and delegates to `__wt_txn_printlog(session, ofile, flags, start_lsn_or_null, end_lsn_or_null)`.

Control flow: The command accumulates `WT_TXN_PRINTLOG_MSG`, `WT_TXN_PRINTLOG_UNREDACT`, and `WT_TXN_PRINTLOG_HEX` flags. It rejects extra operands and malformed LSN strings. By default it leaves user data redacted and only passes the unredact flag when `-u` is explicit.

State and persistence behavior: The command is read-only with respect to database state. It may create/truncate the named output file through the lower printlog implementation. LSN range state is local to the invocation.

Dependencies and integration points: Uses WiredTiger log structures (`WT_LSN`), printlog flags, and the internal transaction log printer. It is a support/diagnostic interface for inspecting recovery logs and customer data while minimizing accidental user-data exposure.

Risks: `sscanf` accepts some partially numeric forms according to C conversion rules; malformed separators are rejected only when the parsed count is not 2 or 4. `-u` can expose application data, while `-x` changes display semantics for downstream parsers. Output file errors depend on `__wt_txn_printlog` handling.

Test signals: Tests should cover default redaction, flag combinations, two-value and four-value LSN forms, bad LSN usage errors, and output-file creation. Integration tests need a database with log records and stable expected output patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_printlog.c -->
