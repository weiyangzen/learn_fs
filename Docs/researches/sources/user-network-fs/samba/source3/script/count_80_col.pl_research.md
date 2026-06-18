# sources/user-network-fs/samba/source3/script/count_80_col.pl

Purpose: tiny Perl style helper that counts lines longer than 80 characters in one file, ignoring `#define` lines.

Important APIs, types, and functions: uses Perl file IO, `length`, regex matching, and `$ARGV[0]`.

Control flow: open input, increment a counter for long non-define lines, close input, print a summary only when count is nonzero, and exit zero.

State and persistence: read-only; no files are written.

Dependencies and integration: requires Perl. It is likely used manually or by style checks.

Risks: no argument validation; a missing file dies. Perl `length` includes the newline, so effective visible width threshold is one character lower than it may appear.

Test signals: run on files with no long lines, long non-define lines, and long define lines.
