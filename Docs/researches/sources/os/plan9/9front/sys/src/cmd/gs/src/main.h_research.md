# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/main.h

## Purpose
Backward-compatible Ghostscript interface wrapper for old single-interpreter clients of `gsmain.c`.

## Main Structure
- Includes `iapi.h`, `imain.h`, and `iminst.h`.
- Contains legacy macro aliases for `gs_init*`, library path setup, file/string execution, and debug stack dumping.
- The entire legacy interface body is disabled by `#if 0`.

## Integration Notes
- Present for compatibility naming and include stability, but exports no active wrappers beyond including the modern API headers.

## Risks and Edge Cases
- Consumers expecting old macros from this header will not get them because the block is disabled.
- Comments preserve historical API migration information but not active behavior.
