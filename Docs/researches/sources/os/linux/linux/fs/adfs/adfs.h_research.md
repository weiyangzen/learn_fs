# File Research: sources/os/linux/linux/fs/adfs/adfs.h

Defines ADFS internal structures, constants, helper macros, and cross-file prototypes.

Key behavior:
- Defines fragment constants for free, bad, and root fragments.
- Defines RISC OS filetype extraction from stamped load addresses.
- Defines ADFS attribute bits for owner/public read/write, locked, directory, and execute state.
- `struct adfs_inode_info` stores parent object id, indirect disk address, RISC OS load/exec addresses, attributes, mmu-private size, and embedded VFS inode.
- `struct adfs_sb_info` stores map state, selected directory operations, uid/gid/masks, filetype suffix option, map geometry, share size, and name length.
- `struct adfs_dir` abstracts a loaded directory across up to inline or allocated buffer-head arrays and format-specific headers/tails.
- `struct object_info` is the common in-memory representation of a directory entry.
- `struct adfs_dir_ops` defines format-specific directory operations.
- Declares inode, map, directory, file, and logging helpers.
- `__adfs_block_map()` maps an object’s block offset through the fragment map, accounting for embedded offset bits in indirect addresses.
- `adfs_map_discrecord()` returns the disk record stored in the map.
- `adfs_disc_size()` builds the 64-bit filesystem size from low/high fields.

Important interactions:
- Shared by every ADFS source file.
- The selected `adfs_dir_ops` implementation is chosen at mount based on disk format version.
