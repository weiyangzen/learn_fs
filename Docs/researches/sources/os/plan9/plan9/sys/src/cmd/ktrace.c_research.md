# File Research: sources/os/plan9/plan9/sys/src/cmd/ktrace.c

Read fully: 403 lines, 7222 bytes. SHA-256 prefix: `85c621c4c9617472`.

This command reconstructs kernel stack traces from a kernel binary, initial PC/SP, optional link register, and either interactive or stdin-provided memory values.

`main()` parses `[-i] kernel pc sp [link]`, initializes the executable header/symbol table, chooses a trace routine based on magic, reads stack address/value pairs from stdin unless interactive, and calls the selected walker. Trace implementations cover RISC-style frame/link handling (`rtrace()`), generic CISC `pc2sp()` unwinding (`ctrace()`), i386 interrupt-frame special cases, and amd64 `_intrr` interrupt-frame handling. `printaddr()` emits `src(...)`-style lines with symbol comments.

Dependencies: Plan 9 `mach` symbols, frame symbol `.frame`, `pc2sp()`, `findsym()`, `findlocal()`, and `symoff()`.

Risk notes: stops after 40 frames and uses architecture-specific heuristics. Noninteractive stack lookup is exact address matching in fixed arrays of 1024 entries.
