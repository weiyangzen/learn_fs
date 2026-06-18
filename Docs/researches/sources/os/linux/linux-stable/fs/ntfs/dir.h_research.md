# File Research: sources/os/linux/linux-stable/fs/ntfs/dir.h

## Scope

This header declares the small public directory interface for the NTFS driver.

## APIs And Data Structures

- `struct ntfs_name` carries a lookup result used by `ntfs_lookup()` to resolve dcache aliasing:
  - `mref`: target MFT reference.
  - `type`: NTFS filename namespace type, especially DOS short-name handling.
  - `len` and flexible `name[]`: optional little-endian Unicode long-name copy.
- `extern __le16 I30[5]` exposes the `$I30` index name shared by directory and index allocation code.
- `ntfs_lookup_inode_by_name()` is declared for name lookup inside directories.
- `ntfs_check_empty_dir()` is declared for deletion/rmdir-style emptiness checks.

## Dependencies

The header includes `inode.h` and is consumed by directory, inode, index-related, and name lookup paths that need the canonical `$I30` name or directory lookup helpers.

## Risks And Invariants

- `struct ntfs_name` is packed and includes a flexible little-endian Unicode tail; callers must allocate enough space for non-DOS names.
- `I30` has global storage and is also used as an identity optimization elsewhere, so code often compares the pointer against `I30` before deciding whether a name buffer needs freeing.
