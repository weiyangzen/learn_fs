# File Research: sources/local-fs/xfsdump/restore/namreg.h

## Summary
Declares the directory-entry name registry API used by the restore tree.

## Main Contents
- `nrh_t` as a 64-bit name-registry handle.
- `NRH_NULL` sentinel.
- `namreg_init()` for creating or resyncing the registry.
- `namreg_add()` to register a non-NUL-terminated name.
- `namreg_del()` to remove a handle, though the implementation is currently a no-op.
- `namreg_map()` to switch to mmap-backed lookups.
- `namreg_get()` to resolve a handle into a caller buffer.

## Risks
The API exposes integer handles that are persistent file offsets; callers must not invent or reuse handles after deletion.

`namreg_get()` has multiple negative error returns, so callers must distinguish short buffer, missing handle, and syscall failure if they want precise recovery.
