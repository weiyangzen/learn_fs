# File Research: sources/os/linux/linux/fs/vboxsf/shfl_hostintf.h

## Purpose
Defines the VirtualBox Shared Folders guest-host ABI used by vboxsf: function numbers, constants, packed metadata structures, create/open flags, and HGCM parameter structures.

## Main Contents
- Protocol function numbers: map/query, create, close, read, write, list, information, remove, map/unmap folder, rename, flush, set UTF-8, readlink, symlink, and set symlink mode.
- Handle constants: `SHFL_ROOT_NIL`, `SHFL_HANDLE_NIL`, `SHFL_MAX_LEN`, `SHFL_MAX_MAPPINGS`, `SHFL_MAX_RW_COUNT`.
- String and metadata structures:
  - `struct shfl_string`: flexible UTF-8/UTF-16 string buffer with size and length.
  - `struct shfl_fsobjattr`, `shfl_fsobjattr_unix`, `shfl_fsobjinfo`: mode bits, Unix attributes, sizes, timestamps, allocation.
  - `struct shfl_dirinfo`: variable-length directory entry.
  - `struct shfl_fsproperties` and `shfl_volinfo`: filesystem/volume properties.
- Mode/type constants mirroring Unix file type and permission bits.
- Create/open ABI:
  - `enum shfl_create_result`.
  - `SHFL_CF_*` lookup, directory, action, access, deny, attribute, and append flags.
  - `struct shfl_createparms`.
- HGCM request parameter structures for map/unmap, create, close, read, write, list, information, remove, rename, readlink, and symlink.

## Important Design Points
- Structures shared with the host are packed or size-asserted using `VMMDEV_ASSERT_SIZE`.
- Variable-length protocol data is represented by offsets/sizes and flexible arrays.
- `shfl_string_buf_size()` centralizes buffer size calculation for host calls.
- Create/open uses result codes and returned handles together; `SHFL_HANDLE_NIL` can indicate an expected non-exceptional failure.

## Cross-File Relationships
- Included by `vfsmod.h`, then used by all vboxsf implementation files.
- `vboxsf_wrappers.c` fills these HGCM parameter structures for host calls.
- `dir.c`, `file.c`, `utils.c`, and `super.c` translate between VFS types and SHFL mode/metadata fields.

## Risks / Review Notes
- This is ABI-sensitive; changing layout, packing, enum values, or function numbers can break host compatibility.
- `struct shfl_dirinfo` is variable-length and can be unaligned when returned by the host; consumers must avoid unsafe assumptions.
- Comments include legacy/Windows-oriented protocol semantics that Linux callers must translate carefully.
