# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/debug.h

## Purpose

Debug/assertion abstraction for the imported FSE/Zstd code. It provides compile-time assertions, optional runtime assertions, and optional logging.

## Main Components

- `DEBUG_STATIC_ASSERT(c)` for function-scope compile-time checks.
- `DEBUGLEVEL`, defaulting to `0`.
- `DEBUGFILE`, defaulting to `stderr`.
- `assert()` behavior:
  - enabled when `DEBUGLEVEL >= 1`
  - compiled to no-op otherwise
- Logging when `DEBUGLEVEL >= 2`:
  - global `g_debuglevel`
  - `RAWLOG`
  - `DEBUGLOG`

## Dependencies

- `<assert.h>` when assertions are enabled.
- `<stdio.h>` when logging is enabled.

## Research Notes

- Default release behavior disables runtime checks and logging.
- `g_debuglevel` is declared but not thread-safe.
- Many codec invariants are guarded by `assert`; with default `DEBUGLEVEL=0`, production safety depends on explicit error checks elsewhere.
