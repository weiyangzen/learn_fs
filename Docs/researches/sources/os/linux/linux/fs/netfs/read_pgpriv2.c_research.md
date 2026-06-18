# File Research: sources/os/linux/linux/fs/netfs/read_pgpriv2.c

Deprecated bridge for copying read folios to cache using `PG_private_2`.

Key responsibilities:
- Creates a copy-to-cache write request when a downloaded folio needs cache storage.
- Appends folios to the write request rolling buffer.
- Splits large folios into cache write subrequests.
- Ends copy-to-cache writes and clears `PG_private_2` as copied ranges complete.

Important APIs:
- `netfs_pgpriv2_copy_to_cache()`.
- `netfs_pgpriv2_end_copy_to_cache()`.
- `netfs_pgpriv2_unlock_copied_folios()`.

Important behavior:
- If cache resources are invalid or write request creation fails, copy-to-cache is disabled for the read request.
- Folios beyond EOF are immediately unmarked.
- Copy writes use stream 1, `NETFS_PGPRIV2_COPY_TO_CACHE`, and offloaded collection.
- Completion clears `PG_private_2` only after collected range reaches the folio end or EOF-limited end.

Note:
- File explicitly marks this path deprecated; newer folio-private mechanisms are preferred elsewhere in netfs.
