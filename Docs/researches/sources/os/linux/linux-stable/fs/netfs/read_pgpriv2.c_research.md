# File Research: sources/os/linux/linux-stable/fs/netfs/read_pgpriv2.c

Deprecated support for copying read folios to cache using `PG_private_2`.

Key behavior:
- Starts a secondary write request with origin `NETFS_PGPRIV2_COPY_TO_CACHE`.
- Marks read folios private_2 and appends them to the copy request rolling buffer.
- Splits a folio into one or more cache write subrequests using `netfs_advance_write()`.
- Flushes outstanding cache writes when the read request finishes.
- Clears private_2 marks as copy-to-cache writeback collection advances.

Status:
- Code comments explicitly mark this path deprecated; newer private folio metadata is preferred.
