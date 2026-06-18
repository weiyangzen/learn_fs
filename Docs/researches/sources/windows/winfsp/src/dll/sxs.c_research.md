# File Research: sources/windows/winfsp/src/dll/sxs.c

Computes the side-by-side identity/suffix for WinFsp DLL deployments.

Initialization:
- `FspSxsIdentInitialize()` runs once via `InitOnceExecuteOnce`.
- First tries `FspSxsIdentInitializeFromFile()`:
  - gets current DLL path from `DllInstance`,
  - changes `.dll` or `-arch.dll` naming into `.sxs`,
  - reads first UTF-8 line,
  - stores separator plus identifier in `FspSxsIdentBuf`.
- Falls back to `FspSxsIdentInitializeFromDirectory()`:
  - opens the DLL and gets final path,
  - scans for `\SXS\SXS.<ident>\`,
  - extracts `<ident>` into the same buffer.

Exported/internal helpers:
- `FspSxsIdent()`: returns identity without separator.
- `FspSxsSuffix()`: returns separator-prefixed suffix.
- `FspSxsAppendSuffix(Buffer, Size, Ident)`: appends current suffix to a supplied identifier, returning `L"<INVALID>"` if the caller buffer is too small.

Important behavior:
- Identifier buffer is small and bounded: 32 plus separator/NUL storage.
- Fallback directory parsing supports SxS layouts even without a companion `.sxs` file.
