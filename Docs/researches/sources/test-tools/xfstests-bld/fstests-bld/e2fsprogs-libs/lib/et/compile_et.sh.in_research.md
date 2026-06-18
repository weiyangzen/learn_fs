# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/compile_et.sh.in

## Purpose
`compile_et.sh.in` is the configured shell driver that turns an `.et` error-table source into generated `.h` and `.c` files.

## Important APIs, Types, and Functions
It uses substituted `@AWK@`, `@datadir@/et`, and `@ET_DIR@`, supports `--build-tree`, and invokes `et_h.awk` and `et_c.awk`.

## Control Flow
The script normalizes locale variables to `C`, locates AWK templates in the installed directory or build tree, validates the input `.et`, generates temporary header/source outputs, compares with existing files, and replaces outputs only when contents changed. New generated files are made read-only.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent state is generated `BASE.h` and `BASE.c`. Dependencies include shell, sed, cmp, mv, chmod, AWK templates, and configure substitution. Risks include the apparent use of `$as_unset` without local definition, whitespace-sensitive `.et` parsing inherited from AWK, and read-only outputs surprising rebuild tools. Test signals are `make check` diffs against test case expected outputs.
