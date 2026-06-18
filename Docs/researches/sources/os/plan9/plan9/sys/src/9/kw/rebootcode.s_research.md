# File Research: sources/os/plan9/plan9/sys/src/9/kw/rebootcode.s

## Role

Standalone ARM reboot trampoline copied to low memory by `main.c:reboot`. It disables caches/MMU, sets temporary mappings, copies replacement code, and jumps to the new entry point.

This is reboot/bootstrap infrastructure, not filesystem code.

## Main Interfaces

- `main(SB)`: reboot trampoline entry.
- `cachesoff(SB)`: disables cache state.
- `_r15warp(SB)`: branch/jump helper.
- `mmudisable(SB)`
- `mmuinvalidate(SB)`
- `cacheuwbinv(SB)`

## Important Behavior

- Runs at a fixed copied location with arguments describing destination entry, source code pointer, and size.
- Copies the supplied code in words.
- Builds or reuses temporary page-table entries enough to execute during transition.
- Flushes and invalidates caches, disables MMU, invalidates TLBs, and jumps to the new entry.

## Dependencies And Assumptions

- Includes `arm.s`.
- Must stay position-safe enough for copying/execution as reboot code.
- Called by `reboot` in `main.c`.

## Notable Risks

- Any cache/MMU mistake can hang the machine during reboot.
- Source/destination size assumptions are raw and unchecked at this level.
