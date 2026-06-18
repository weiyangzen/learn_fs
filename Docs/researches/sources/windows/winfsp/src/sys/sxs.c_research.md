# File Research: sources/windows/winfsp/src/sys/sxs.c

## Purpose

`sxs.c` extracts and exposes a side-by-side identity/suffix from the loaded driver name. This lets WinFsp derive variant-specific naming when the driver binary name contains the configured side-by-side separator.

## Main Contents

- Static buffer `FspSxsIdentBuf`.
- Static strings:
  - `FspSxsIdentStr`
  - `FspSxsSuffixStr`
- Public functions:
  - `FspSxsIdentInitialize`
  - `FspSxsIdent`
  - `FspSxsSuffix`

## Behavior

`FspSxsIdentInitialize`:

- Scans backward through `DriverName`.
- Stops at a path separator or at `FSP_SXS_SEPARATOR_CHAR`.
- If no side-by-side separator is found in the final path component, leaves identity empty.
- Copies from the separator through the end into `FspSxsIdentBuf`, capped to the static buffer size.
- Sets:
  - ident string to skip the first copied character,
  - suffix string to include the separator.

`FspSxsIdent` returns the identity string.

`FspSxsSuffix` returns the suffix string.

## Notable Details

- The static `UNICODE_STRING` buffers are initialized so `Ident` starts at `FspSxsIdentBuf + 1`, while `Suffix` starts at the separator.
- Initialization is marked `INIT`, so it is intended only during driver initialization.
