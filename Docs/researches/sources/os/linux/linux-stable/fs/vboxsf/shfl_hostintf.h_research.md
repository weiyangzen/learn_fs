# File Research: sources/os/linux/linux-stable/fs/vboxsf/shfl_hostintf.h

Defines the VirtualBox Shared Folders host-interface ABI used by the vboxsf driver. It contains function numbers, handles, mode bits, packed wire structs, parameter counts, and helper constants for calls such as map/unmap folder, create/open, close, read, write, list directory, get/set information, remove, rename, readlink, symlink, UTF-8 selection, and symlink mode selection.

Important data structures:
- `shfl_string`: variable-length UTF-8/UTF-16 path string with explicit byte size and length.
- `shfl_fsobjattr` and `shfl_fsobjinfo`: host object attributes, sizes, timestamps, mode, and optional Unix/EA metadata.
- `shfl_createparms`: bidirectional create/open request containing returned handle, result code, flags, and object info.
- HGCM parameter structs such as `shfl_create`, `shfl_read`, `shfl_write`, `shfl_list`, and `shfl_information`.

The file is ABI-sensitive: many structs are `__packed`, size assertions are used, and values mirror VirtualBox host service expectations. Executable driver code depends on these definitions for correct pointer direction, parameter counts, flag translation, and buffer sizing.
