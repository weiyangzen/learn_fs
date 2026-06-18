# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tc.c

Chooses delimiter characters for troff field alignment.

Key functions:
- `choochar` scans all real cell text for used ASCII bytes, then selects two unused characters from a prioritized `COMMON` string.
- `point` distinguishes real string pointers from small integer diversion/register identifiers stored as pointer values.

Notable behavior:
- Fails if no two suitable delimiter characters are available.
- Only scans bytes below 128; non-ASCII bytes do not affect delimiter choice.
