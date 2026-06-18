# File Research: sources/local-fs/squashfs-tools/squashfs-tools/date.c

Implements date-string parsing by delegating to the system `date` command.

Main function:
- `exec_date(char *string, unsigned int *mtime, char **error)`

Behavior:
- Creates a pipe and forks.
- Child redirects stdout/stderr to the pipe and runs `/usr/bin/date -d <string> +%s`.
- Parent reads command output, waits for child, parses seconds since epoch, and validates the result fits unsigned 32-bit SquashFS time.
- Rejects negative times and times on/after `2^32`.

Dependencies:
- Uses external `read_bytes()`.
- Uses `ASPRINTF()` for error strings.

Notable risks/quirks:
- Hard-codes `/usr/bin/date` and GNU-style `-d`.
- Reads into an 11-byte buffer and validates output length before parsing.
