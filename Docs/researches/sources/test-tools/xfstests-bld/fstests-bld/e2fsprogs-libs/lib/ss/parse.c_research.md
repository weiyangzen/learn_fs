# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/parse.c

## Purpose
`parse.c` tokenizes ss command lines into argv arrays.

## Important APIs, Types, and Functions
The public function is `ss_parse()`. It uses `enum parse_mode` with `WHITESPACE`, `TOKEN`, and `QUOTED_STRING`.

## Control Flow
The parser walks the input in place, allocates/grows a NULL-terminated argv array, splits on spaces/tabs, treats quotes as grouping delimiters, converts doubled quotes inside quoted strings to a literal quote, and reports unbalanced quotes via `ss_error()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller's mutable command buffer and returned argv array. Dependencies include realloc/malloc and ss error reporting. Risks include no backslash escaping, destructive input mutation, unchecked realloc failure after the first allocation, and NULL return handling by callers. Test signals are `test_ss` scripts with quoted and spaced arguments and unbalanced-quote diagnostics.
