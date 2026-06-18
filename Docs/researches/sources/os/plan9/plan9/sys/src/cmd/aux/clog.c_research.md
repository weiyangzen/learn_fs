# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/clog.c

This file implements a simple console logger.

Key behavior:
- Opens a console-like input file and an append log file.
- Reads complete newline-terminated lines with `Biobuf`.
- Prefixes each line with a timestamp and appends it to the log.
- Reopens the log on write failure and retries.

Important details:
- Creates the log file with `DMAPPEND|0666` if needed.
- Drops overlong partial-line fragments by reading and discarding extra buffered data.
- Stops on true EOF or read error.

Filesystem relevance:
- Indirect: consumes and writes ordinary files, typically device console streams and log files.
