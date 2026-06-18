# File Research: sources/os/plan9/9front/sys/src/cmd/dial/expect.c

Purpose: Waits for a good string on stdin while optionally failing on any bad string.

Key behavior:
- Options: `-i` ignore case, `-q` quiet, `-t secs` timeout.
- Requires one good string and any number of bad strings.
- Opens `/dev/cons` and echoes incoming data there unless quiet, stripping carriage returns.
- Maintains a rolling buffer large enough to catch matches spanning reads.
- On good match, exits success.
- On bad match, exits with the bad string.
- On EOF, exits `"EOF"`.

Notable details:
- The timeout is implemented with `alarm(timeout*1000)` and a note handler that exits with the note string.
