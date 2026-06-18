# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/tran.c

Symbol table and awk value conversion layer.

Initializes built-in variables including `FS`, `RS`, `OFS`, `ORS`, `OFMT`, `CONVFMT`, `NF`, `NR`, `FNR`, `FILENAME`, `SUBSEP`, `RSTART`, `RLENGTH`, `SYMTAB`, `ARGV`, and optionally `ENVIRON`.

Provides hash-table backed arrays and cells:

- `makesymtab`, `setsymtab`, `lookup`, `rehash`
- `freesymtab`, `freeelem`
- `setfval`, `setsval`
- `getfval`, `getsval`
- `tostring`, `qstring`

The file enforces awk’s dual string/numeric value model and coordinates record/field invalidation when `$0`, `$n`, or `NF`-related values change.
