# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2.h

This header defines the newer UFS quota2 on-disk metadata format.

Key contents:
- Defines `struct quota2_val` for hard/soft limits, current usage, expiry, and grace time.
- Defines quota value classes `QL_BLOCK` and `QL_FILE`.
- Defines `struct quota2_entry`, storing block/file values plus linked-list and uid data.
- Defines `struct quota2_header`, including magic, quota type, hash table sizing, default entry, free list head, and variable hash heads.
- Defines superblock flags for enabled quota2 types.
- Defines offset/index conversion macros.
- Declares quota2 block creation, free-list setup, byte-swap helpers, and limit-checking.

Role:
- Metadata-integrated quota implementation intended to be fsck- and journal-visible.
