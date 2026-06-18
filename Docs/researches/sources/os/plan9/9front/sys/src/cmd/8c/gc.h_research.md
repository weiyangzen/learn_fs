# File Research: sources/os/plan9/9front/sys/src/cmd/8c/gc.h

This is the shared private header for the 386 C compiler backend.

Key responsibilities:
- Includes common C compiler definitions and the 386 object format.
- Defines 386 data-model sizes and `FNX` complexity marker for function-call expressions.
- Declares backend structures:
  - `Adr` and `Prog` for generated object instructions.
  - `Case`/`C1` for switch lowering.
  - `Var`, `Reg`, and `Rgn` for register optimization.
  - `Renv` for register/environment save state.
- Exposes backend globals for code stream, pc, cases, string literal buffer, register usage, register allocation analysis, live-variable sets, loop data, and optimizer regions.
- Declares function prototypes across `sgen.c`, `cgen.c`, `cgen64.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, `peep.c`, and arithmetic helpers.
- Defines bitset/liveness helper macros such as `LOAD`, `STORE`, `CLOAD`, `CREF`, and `LOOP`.

Integration points:
- Included by nearly every `8c` backend file.
- Couples the compiler backend tightly to `8.out.h` instruction and operand constants.
- `#pragma varargck` entries align Plan 9 formatters with custom conversion functions.

Risks and invariants:
- Many globals are shared mutable state; backend phases must run in expected order.
- The `rplink` macro reuses a generic node field, documented as a deliberate field steal.
