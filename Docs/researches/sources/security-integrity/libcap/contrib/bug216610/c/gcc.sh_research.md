<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh -->
# sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh

## Purpose
GCC wrapper that works around Go internal linker issues with RIP-relative `.rodata.*` references in `.syso` object files.

## Important APIs, Types, And Functions
Uses environment variable `GCC`, arrays `args`, `final`, and `ses`, GCC `-S`, `sed -i`, and final GCC invocation.

## Control Flow
Collects compiler flags until the first `.c` input, compiles each C file to assembly, rewrites `.rodata.*` section directives to `.text`, replaces C inputs with assembly paths, invokes GCC on the adjusted command line, and deletes intermediate `.s` files on success.

## State And Persistence Behavior
Creates temporary `.s` files and output objects requested by the original arguments. Removes intermediate assembly after successful compilation.

## Dependencies And Integration Points
Used by bug216610 make targets for native and cross `.syso` builds.

## Risks And Edge Cases
Argument parsing is fragile: flags after the first `.c` are not part of the C-to-assembly pass. Rewriting all matching `.rodata.*` lines to `.text` is broad and architecture/toolchain-sensitive.

## Test Signals
Signals are successful `.syso` generation and Go linker correctness when calling C functions.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh -->
