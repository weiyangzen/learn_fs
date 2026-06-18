# File Research: sources/local-fs/xfsprogs/libxfs/xfs_trans_resv.h

This header defines transaction reservation data structures, standard log count constants, and the public reservation calculation API.

`struct xfs_trans_res` stores one reservation class: log bytes per ticket, number of log operations per ticket, and log flags such as permanent reservation. `struct xfs_trans_resv` aggregates all mount-level reservation classes: writes, truncates, namespace operations, inode free/change, growdata/growrt, attributes, quotas, superblock updates, fsync timestamp updates, and atomic write completion.

`M_RES(mp)` provides shorthand access to the mount reservation table. Directory operation reservation/count macros model directory data/free/btree blocks plus bmap btree requirements. Log count constants define default and operation-specific ticket counts, while the old reflink constants are retained only for minimum log size calculations.

The exported functions include full mount reservation calculation, allocation/free block counting, finish reservations for BUI/EFI/RUI/CUI and their realtime variants, minimum-log-size calculators, and atomic write reservation/log geometry functions.
