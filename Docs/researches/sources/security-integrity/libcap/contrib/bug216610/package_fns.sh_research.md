<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/package_fns.sh -->
# sources/security-integrity/libcap/contrib/bug216610/package_fns.sh

## Purpose
Generates Go linkname wrapper code for exported functions found in a `.syso` object.

## Important APIs, Types, And Functions
Validates arguments, emits `package`, imports `unsafe`, declares `func syso`, `sysoCaller`, and for each `objdump` function symbol emits `//go:linkname`, a byte symbol, and a `syso__<sym>` caller.

## Control Flow
Checks the second argument is a `.syso`, prints common wrapper boilerplate, scans `objdump -x` for global function symbols, and prints one wrapper variable per symbol.

## State And Persistence Behavior
Writes generated Go source to stdout. Does not modify the `.syso`.

## Dependencies And Integration Points
Used by bug216610 makefile to create `go/fibber/linkage.go`.

## Risks And Edge Cases
Parsing `objdump` output by columns is toolchain-sensitive. `go:linkname` requires unsafe import behavior and symbol names must match exactly.

## Test Signals
Signals are generated `syso__fib_init` and `syso__fib_next` wrappers that compile and work.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/package_fns.sh -->
