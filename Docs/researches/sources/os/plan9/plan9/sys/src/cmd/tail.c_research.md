# File Research: sources/os/plan9/plan9/sys/src/cmd/tail.c

This file implements `tail`, including POSIX options and V10 reverse mode.

Key behavior:
- Supports `-n`, `-c`, `-f`, `-r`, and legacy `+-N[bc][fr]` syntax.
- Handles seekable and non-seekable inputs differently.
- For seekable files, seeks from beginning/end or scans backward for line tails.
- For pipes, either skips from the beginning or keeps a rolling tail buffer.
- `-f` repeatedly copies appended data and detects truncation.

Important details:
- Reverse mode is incompatible with character units, follow mode, and begin-origin mode.
- Follow mode uses `dirfstat` to detect shrinking files and seek back to start.
- Output is buffered but flushed during forward copy to support pipes.

Filesystem relevance:
- Direct file-reading utility with explicit behavior for pipes, seekable files, and truncating files.
