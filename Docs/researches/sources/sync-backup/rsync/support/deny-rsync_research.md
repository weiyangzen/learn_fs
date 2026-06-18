<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/deny-rsync -->
# sources/sync-backup/rsync/support/deny-rsync

Purpose: shell helper that emits a minimal rsync protocol error response to a non-daemon client and exits with a refusal-style code.

Important APIs/types/functions: `byte_escape()` formats numeric bytes; globals are `protocol_version=29` and `exit_code=4`. The payload mimics `rprintf(FERROR_XFER, "%s\n", msg)` in rsync's multiplexed protocol.

Control flow: take the first argument as the message, truncate it to fit a simple one-byte length, write protocol version and zero checksum seed as little-endian four-byte values, write a multiplexed error header and message, sleep one second so the client receives the error, and exit 4.

State and persistence behavior: no persistent state. It writes binary protocol bytes to stdout and diagnostic semantics are carried by the client-side rsync.

Dependencies and integration points: depends on bash, `printf`, `echo -ne`, and rsync protocol framing. It is useful as a forced command or policy denial shim.

Risks: protocol version and framing are intentionally naive and fixed; newer clients may behave differently. It supports only short messages and does not escape arbitrary binary data. `echo -E` behavior is shell-dependent but acceptable under bash.

Test signals: invoke via an rsync remote-shell/forced-command path and verify the client displays the supplied message rather than a generic broken-pipe failure and receives exit code 4 semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/deny-rsync -->
