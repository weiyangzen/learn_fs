<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_salvage.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_salvage.c

Purpose: Implements `wt salvage`, invoking WiredTiger salvage on a file URI, optionally with force.

Important APIs/functions: `usage` documents `salvage [-F] uri`. `util_salvage` parses `-F`, resolves the operand as a file URI, and calls `session->salvage(session, uri, force)` where `force` is either `NULL` or the string `"force"`.

Control flow: The command accepts exactly one URI after options. It reports `session.salvage` errors through `util_err`; on success with verbose progress enabled it prints a newline to finish the progress line.

State and persistence behavior: This is a mutating recovery/repair operation. It can rewrite or reconstruct on-disk file contents according to WiredTiger salvage semantics, and `-F` bypasses basic refusal behavior for damaged files.

Dependencies and integration points: Uses public `WT_SESSION::salvage`, the shared URI resolver, shared usage and error helpers, and global `verbose`. It is an administrative repair command in the `wt` utility.

Risks: Salvage can discard unrecoverable data, and forced salvage increases that risk. Passing `"force"` as a bare config string depends on WiredTiger configuration parsing accepting that shorthand. Operators need clear backups before use.

Test signals: Tests should verify option parsing, forced versus default config passed to a mocked session, verbose newline behavior, and real salvage behavior on intentionally damaged test files where practical.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_salvage.c -->
