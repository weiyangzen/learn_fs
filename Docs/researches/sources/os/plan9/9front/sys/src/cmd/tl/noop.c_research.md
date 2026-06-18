# File Research: sources/os/plan9/9front/sys/src/cmd/tl/noop.c

`noop.c` rewrites pseudo-instructions and normalizes instruction streams before span/code emission.

Main phase:
- `noops()`:
  - Finds leaf functions.
  - Computes frame and become sizes.
  - Removes NOPs.
  - Expands `RET` and `BECOME`.
  - Emits prologues/epilogues.
  - Handles Thumb stack/register constraints.
  - Rewrites division/modulo pseudo-ops into helper calls.
  - Converts some branch-through-register forms for Thumb/ARM interworking.

Helpers:
- `movrr()` builds register moves.
- `fnret()` emits return via `MOVW` or `ABXRET`.
- `aword()` / `adword()` inject raw words/dwords.
- `nocache()` clears cached operand class/op selection.

Division support:
- `initdiv()` resolves `_div`, `_divu`, `_mod`, `_modu`.
- `setdiv()` marks helper symbols as foreign when ARM/Thumb domains differ.
- `divsig()` and `sigdiv()` set internal signatures for helper symbols.
- `sdiv()` marks dynamic imports for DLM mode.

Risk notes:
- Thumb interworking code is complex and depends on `seenthumb`, `foreign`, `fnptr`, and `CALLEEBX`.
- Some become paths explicitly diagnose unsupported foreign/Thumb cases.
- Division expansion assumes stack layout and helper calling convention.
