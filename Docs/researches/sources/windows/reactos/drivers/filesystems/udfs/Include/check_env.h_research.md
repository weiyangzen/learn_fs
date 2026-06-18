# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/check_env.h

## Purpose

`check_env.h` detects and validates the execution environment for shared UDFS/CDRW code: NT kernel mode, NT native mode, or Win32 mode.

## Main Contents

- Contains an older, fully commented environment-selection block showing intended include policy for kernel/native/Win32 builds.
- Defines `NT_KERNEL_MODE` when `NT_INCLUDED` is already set.
- Leaves `USER_MODE` definitions commented out for NT native and Win32 cases.
- Defaults to `WIN_32_MODE` when neither NT kernel nor NT native mode is selected, or when `WIN_32_MODE` is explicitly defined.
- Emits preprocessor errors if:
  - `NT_KERNEL_MODE` is combined with `NT_NATIVE_MODE` or `WIN_32_MODE`.
  - `NT_NATIVE_MODE` is combined with `WIN_32_MODE`.

## Integration Notes

This header should be included before environment-specific headers to prevent conflicting build-mode definitions.

## Risks And Edge Cases

- Much of the original include logic is commented out, so this file now mostly validates macros rather than including the right platform headers.
- Defaulting to Win32 mode can hide missing mode definitions unless build scripts set explicit symbols.
