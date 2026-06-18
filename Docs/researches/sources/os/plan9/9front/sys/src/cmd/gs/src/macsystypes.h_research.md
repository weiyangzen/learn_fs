# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macsystypes.h

## Purpose
Mac CodeWarrior replacement for generated `sys/types.h` during project generation/build.

## Main Content
- Include guard `__sys_types_h__`.
- Includes `<MacTypes.h>` and `<unix.h>`.
- Defines `CHECK_INTERRUPTS`.
- Defines `GX_COLOR_INDEX_TYPE UInt64`.
- Renames `main` to `gs_main`.
- Ensures `__MACOS__` is defined.

## Integration Notes
- Copied by `macos-mcp.mak` to `obj/sys/types.h`.
- Provides Mac system typing and build macros expected by Ghostscript portability wrappers.

## Risks and Edge Cases
- `main` macro replacement affects all included compilation units and must be scoped to this build mode.
- Uses CodeWarrior/Mac-specific headers that are not portable to modern non-CodeWarrior toolchains.
