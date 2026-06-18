# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/CrossNt/CrNtDecl.h

## Purpose

`CrNtDecl.h` is a macro-expansion helper used by CrossNt to declare, define, or initialize dynamically resolved NT kernel compatibility function pointers.

## Main Contents

- Clears prior `CROSSNT_DECL` and `CROSSNT_DECL_EX` definitions.
- Under `CROSSNT_DECL_API`, expands declarations into:
  - function pointer typedefs.
  - `extern "C"` function pointer globals named `CrNt<name>`.
  - fallback implementation prototypes named `CrNt<name>_impl`.
- Under `CROSSNT_DECL_STUB`, expands declarations into initialized `CrNt<name> = NULL` pointer globals.
- Under `CROSSNT_INIT_STUB`, expands declarations into runtime initialization code:
  - logs the current pointer.
  - resolves the symbol from `NTOSKRNL.EXE` or a specified module.
  - falls back to `CrNt<name>_impl` when resolution fails.

## Integration Notes

This file is not useful alone. It is included around `CrNtStubs.h` after defining one of the expansion modes. That allows a single symbol list to generate declarations, storage, and initialization code.

## Risks And Edge Cases

- The macro system is fragile: wrong include order or missing mode macro changes emitted code.
- The `CROSSNT_INIT_STUB` branch has a suspicious debug format string in the non-EX macro: `final %\n` appears malformed.
- The code assumes `CrNtGetProcAddress`, module handles, and fallback implementations exist in the including translation unit.
