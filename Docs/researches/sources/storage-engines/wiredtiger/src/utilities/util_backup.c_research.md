## sources/storage-engines/wiredtiger/src/utilities/util_backup.c

Purpose: implements `wt backup`, copying WiredTiger backup cursor files into a target directory, optionally restricted to named targets.

Important APIs/types/functions: `util_backup` parses `-t uri` options into a `target=(...)` backup cursor config string, opens `session->open_cursor(session, "backup:", ...)`, iterates file names from the backup cursor, and calls static `copy`. `copy` builds `directory/name` and uses internal `__wt_copy_and_sync` to copy and sync files safely.

Control flow: option parsing accumulates comma-separated quoted targets in a scratch buffer. Exactly one positional destination directory is required. After opening `backup:`, the command loops `cursor->next` and `cursor->get_key`; each file is copied, and `WT_NOTFOUND` terminates normally. Scratch memory is freed on all exits, but the cursor is not explicitly closed in this function and relies on session cleanup.

State and persistence behavior: creates filesystem copies of WiredTiger files in the supplied directory. The backup cursor stabilizes the list of files; `__wt_copy_and_sync` handles durability-sensitive copy behavior. The command does not create the destination directory and does not remove partial copies on failure.

Dependencies and integration points: integrates with WiredTiger backup cursor implementation, incremental/hot backup machinery in the engine, filesystem helpers, global `home` and `verbose` output, and `util_err`-style error reporting.

Risks: target config is assembled by quoting raw CLI target strings; unusual quotes or commas in URIs could stress config parsing. Destination path allocation is based on string lengths and assumes a simple slash separator. A mid-copy error leaves a partial backup directory for the operator to clean up. Not explicitly closing the backup cursor could delay release until session close, though the command exits immediately after.

Test signals: full backup smoke tests comparing copied files with a reopenable database, targeted backup tests for `-t`, missing destination argument usage, invalid target errors, verbose output, destination permission errors, and failure injection around `__wt_copy_and_sync`.
