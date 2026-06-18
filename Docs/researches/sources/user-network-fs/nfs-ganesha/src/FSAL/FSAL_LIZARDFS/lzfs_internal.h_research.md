# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/lzfs_internal.h

Purpose: Defines the private ABI for the LizardFS FSAL, including module/export/handle/fd/key/DS structs, constants, supported attribute mask, and cross-file helper prototypes.

Important APIs and types: Important structs are `lzfs_fsal_module`, `lzfs_fsal_export`, `lzfs_fsal_fd`, `lzfs_fsal_state_fd`, `lzfs_fsal_key`, `lzfs_fsal_handle`, `lzfs_fsal_ds_wire`, and `lzfs_fsal_ds_handle`. Constants include LizardFS version encoding, special inode ids, name/block/chunk sizes, max regular inode, supported attrs, largest pNFS stripe count, expected backup DS count, and TCP protocol number.

Control flow: The header wires implementation units together: main/export code uses export ops prototypes; handle code uses handle constructor/destructor and pNFS hooks; DS/MDS code uses DS wire structs; ACL code uses internal get/set helpers; all files share error/context helpers.

State and persistence: It defines where runtime state lives: export owns `liz_t`, root handle, fileinfo cache, pNFS flags, cache settings, and init params; handles own inode, unique key, fd, export pointer, and share counters; DS handles own inode plus cache entry.

Dependencies and integration: Includes Ganesha FSAL API/commonlib, LizardFS C API, and `fileinfo_cache.h`. This makes the FSAL private implementation tightly coupled to both Ganesha internals and LizardFS client ABI.

Risks: `lzfs_fsal_ds_wire` uses `uint32_t inode`; if `liz_inode_t` changes or exceeds 32 bits, pNFS DS handles truncate. Special inode constants and `MAX_REGULAR_INODE` encode LizardFS-specific assumptions. `LZFS_SUPPORTED_ATTRS` includes ACL support, so ACL conversion must remain reliable. Constants such as `LZFS_BIGGEST_STRIPE_COUNT` and expected backup DS count directly shape wire layouts and buffer sizes.

Test signals: Compile against LizardFS API versions, assert inode type/size assumptions, verify special inode behavior for root and metadata files, pNFS layout encoding for large files near stripe limits, and attribute mask behavior against client GETATTR/SETATTR.
