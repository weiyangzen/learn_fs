# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/wrbio.c

Appender for account biography records.

Key responsibilities:
- Opens or creates the bio file.
- Seeks to end and appends one pipe-separated record.
- Fills absent post id/name/dept as empty strings.
- Defaults first email to the username if absent.
- Writes all present email fields.

Dependencies:
- Uses `Acctbio`, `Nemail`, and shared `error`.
