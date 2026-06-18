# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.h

This header defines the in-core state used by live nlink checking and repair.

Key structures:
- `struct xchk_nlink_ctrs`: global state for one live nlink scrub/repair run. It owns the sparse `xfarray` of link observations, mutex, collection and comparison inode scans, directory update hook, orphanage adoption state, and a reusable name buffer.
- `struct xchk_nlink`: per-inode observed counters:
  - `parents`: forward links from parent directories to this inode.
  - `backrefs`: child-directory `..` or parent-pointer references back to this directory.
  - `children`: forward links from this directory to child directories plus dot-related accounting.
  - `flags`: sparse-record lifecycle state.

Flags:
- `XCHK_NLINK_WRITTEN`: record has been initialized/stored.
- `XCHK_NLINK_COMPARE_SCANNED`: record was compared during scrub.
- `XREP_NLINK_DIRTY`: record already participated in repair.

The inline `xchk_nlink_total` computes the expected VFS link count from observations. It adds:
- all parent links,
- one dot link for linked directories,
- child directory links.

The file also documents the accounting model with a root/subdirectory example, which is essential for understanding why parent, backref, and child counts are tracked separately.
