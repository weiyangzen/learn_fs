# File Research: sources/os/plan9/9front/sys/src/cmd/5l/noop.c

This file rewrites the `5l` instruction stream after branch following and before final span. It removes no-ops, detects leaf functions, expands prologues/returns, handles `BECOME`, and lowers integer division/modulo pseudo-ops into helper calls.

Key elements:
- `noops()` performs all main transformations.
- First pass:
  - Tracks maximum frame usage and `BECOME` requirements per text symbol.
  - Marks functions as leaf until calls or division helper needs disprove it.
  - Removes `ANOP` instructions.
  - Retargets branches that point at NOP chains.
- Second pass:
  - Increases caller frame sizes when calls may require max become space.
- Third pass:
  - Emits link-register save/prologue stores for non-leaf or framed functions.
  - Rewrites `RET` into branch-to-link for leaf/no-frame functions or stack-pop-to-PC for normal functions.
  - Rewrites `BECOME` into stack restore plus branch.
  - Patches an old 5c/VFP compatibility sequence around unsigned-to-double conversion.
  - Expands `DIV`, `DIVU`, `MOD`, and `MODU` register operations into stack argument setup, `BL` to helper, result move, and stack cleanup.
- `initdiv()`, `divsig()`, `sigdiv()`, and `sdiv()` resolve or mark division helper symbols `_div`, `_divu`, `_mod`, and `_modu`.
- `nocache()` clears cached optab and operand class fields after mutation.

Dependencies and integration:
- Uses text/prog/symbol state from `l.h`.
- Relies on helper routines from object loading and branch patching.
- Division helper targets are later resolved by `patch()`/`span()`/`asmout()`.

Notable behavior:
- Leaf functions with no autosize can avoid saving the link register.
- `ALEFbecome` is defined to the maximum become space discovered.
- DLM mode can import division helpers instead of requiring local text definitions.

Research notes:
- Despite the filename, this is a major code-shaping pass, not just no-op cleanup.
