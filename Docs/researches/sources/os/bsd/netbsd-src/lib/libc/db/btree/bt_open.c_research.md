# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/bt_open.c

Read completely: 429 lines.

This implements btree open/initialization. It validates `BTREEINFO`, allocates `BTREE` and `DB`, opens a disk or temporary backing file, reads and validates existing metadata or creates new metadata, chooses page/cache sizes, computes overflow thresholds, opens mpool, registers byte-swap filters, creates the root page if needed, and installs DB method pointers.

Important interactions: central setup for all btree operations. It controls byte order, duplicate policy, in-memory mode, read-only mode, mpool cache sizing, and the DB_LOCK/DB_SHMEM/DB_TXN flags.

Security/reliability notes: rejects invalid metadata magic/version/page size/flags with `EFTYPE`. Cache-size rounding and overflow-threshold calculation are guarded with `_DBFIT`, but database file corruption remains a key risk boundary.
