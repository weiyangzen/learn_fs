# File Research: sources/os/bsd/netbsd-src/sys/kern/genlintstub.awk

## Purpose
AWK generator used by kernel Makefiles to create C lint stubs from specially formatted comments in assembly files.

## Main Interfaces
- Recognizes `LINTSTUB: Empty`, `Func`, `Var`, `include`, and `Ignore` directives.
- `process_word(i)` trims semicolons or comment terminators while scanning declarations.
- `error(msg)` records malformed directives and reports line-specific diagnostics.
- `END` exits nonzero if any directive errors were seen.

## Dependencies
Consumes comments embedded in `.S` files and emits C suitable for lint checking. It assumes function stub return types are only `void`, `int`, or `long`.

## Implementation Notes
Generated output begins with repeated “do not edit” notices. Function directives emit `/* ARGSUSED */`, a stub function body, and a synthetic `return(0)` for `int`/`long`. Include directives pass through as literal `#include` lines.

## Research Notes
This script is build-tooling support rather than runtime kernel code. Its main risk is parser brittleness: comments must match the exact directive spelling and tokenization expected by the AWK patterns.
