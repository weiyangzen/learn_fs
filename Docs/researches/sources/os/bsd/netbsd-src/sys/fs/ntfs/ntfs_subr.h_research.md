# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.h

Private NTFS helper header defining internal attribute state and helper prototypes.

Key contents:
- `struct ntvattr`:
  - Represents one NTFS attribute extent.
  - Stores vnode/ntnode pointers, type/name, compression state, data/allocation sizes, VCN range, attribute index, and either run arrays or resident attribute-specific pointers.
- Macros for `ntvattr` union fields.
- Prototypes for:
  - Fixup processing and runlist parsing.
  - Plain and compressed attribute read/write paths.
  - Time conversion.
  - Directory lookup/enumeration.
  - Attribute conversion, lookup, loading, and release.
  - ntnode lookup/refcount/lifetime.
  - `$UpCase` table lifecycle.
  - UTF-8 conversion callbacks.

Role:
- This is the primary internal contract for `ntfs_subr.c`, VFS mount setup, and vnode ops.
