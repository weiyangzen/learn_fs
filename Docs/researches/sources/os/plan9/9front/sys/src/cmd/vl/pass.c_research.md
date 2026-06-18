# File Research: sources/os/plan9/9front/sys/src/cmd/vl/pass.c

This file performs data layout, control-flow following, branch patching, and small numeric utilities.

Key behavior:
- `dodata` validates data initializers, optionally marks string constants, lays out small data first, then larger data, then bss, and creates literal-pool data for large constants/symbol addresses.
- Defines linker symbols such as `setR30`, `bdata`, `edata`, `end`, and `etext`.
- `undef` reports unresolved external symbols.
- `follow` rebuilds the program order from text symbols through `xfol`, reducing jumps and arranging fall-throughs.
- `xfol` follows unconditional jumps, copies short instruction sequences when useful, inverts conditional branches when needed, and preserves `NOSCHED` regions.
- `patch` resolves symbolic branch/jump/return targets, builds forward skip links, and collapses chains of jumps through `brloop`.
- Includes `atolwhex` and `rnd`.

Integration and risks:
- Literal pooling rewrites instruction operands and must clear optab caches.
- Branch following and copying are sensitive to labels, `FOLL`, `NOSCHED`, and delay-slot expectations.
