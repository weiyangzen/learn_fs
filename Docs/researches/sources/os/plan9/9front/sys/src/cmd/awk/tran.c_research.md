# File Research: sources/os/plan9/9front/sys/src/cmd/awk/tran.c

This file implements awk symbol-table and value conversion machinery.

Major responsibilities:
- Initializes built-in variables: `FS`, `RS`, `OFS`, `ORS`, `OFMT`, `CONVFMT`, `FILENAME`, `NF`, `NR`, `FNR`, `SUBSEP`, `RSTART`, `RLENGTH`, `SYMTAB`.
- Builds `ARGV`/`ARGC` from command-line inputs.
- Lazily initializes `ENVIRON` from Plan 9 `/env`, skipping function variables named `fn#...`.
- Implements hash-table arrays: `makesymtab`, `setsymtab`, `lookup`, `freeelem`, `freesymtab`, `rehash`.
- Handles awk cell string/number duality through `setfval`, `setsval`, `getfval`, `getsval`.

Notable implementation details:
- `Cell` values track flags such as `NUM`, `STR`, `ARR`, `CON`, `DONTFREE`, `FLD`, and `REC`.
- Assigning to fields and `$0` invalidates the reciprocal cached representation.
- `SYMTAB` is exposed by storing the main `symtab` pointer in a cell marked `ARR`.
- `qstring` decodes awk string literals, including octal escapes.

Risks and caveats:
- `getsval` uses a fixed `char s[100]` buffer with a source comment noting it is unchecked.
- Environment import is Plan 9-specific and depends on `/env`.
- String ownership depends on `DONTFREE`; incorrect flag handling can leak or free wrong storage.
