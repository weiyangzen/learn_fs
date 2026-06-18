# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/list.c

Purpose: formatting and diagnostics for 386 linker instructions, operands, registers, and strings.

Key behavior: installs formatters; `Pconv` prints full instructions; `Dconv` prints addressing forms including branches, symbols, constants, indirection, and index registers; `Rconv` maps register numbers; `Sconv` escapes string constants; `diag` reports errors with current text symbol context.

Integration notes: used heavily by debug modes and error paths in `obj.c`, `pass.c`, `span.c`, and `asm.c`. `Dconv` temporarily rewrites `D_ADDR` during formatting, so callers rely on restoration.
