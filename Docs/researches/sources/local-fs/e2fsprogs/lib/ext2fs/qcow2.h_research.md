# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.h

Defines qcow2 format constants and structures used by `qcow2.c`: header layout, L2 cache nodes, refcount bookkeeping, and the aggregate `ext2_qcow2_image` state.

Includes magic/version constants, copied/compressed flags, error codes for compressed/encrypted/corrupt images, and prototypes for `qcow2_read_header()` and `qcow2_write_raw_image()`.

Some structures such as L2 cache and refcount state are broader than the current converter’s read-only use, suggesting shared or historical support for qcow2 generation paths.
