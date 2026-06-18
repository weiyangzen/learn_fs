# File Research: sources/os/bsd/netbsd-src/lib/libcurses/inwstr.c

Implements wide string extraction: `inwstr`, `innwstr`, movement variants, `winwstr`, and `winnwstr`.

`winnwstr` normalizes the cursor from a continuation cell to the leading wide cell, then copies base `wchar_t` values across complete cells until EOL or the bounded limit, appending `L'\0'`. It returns `OK` for unbounded calls and the copied count for bounded calls.
