# File Research: sources/os/linux/linux-stable/fs/netfs/read_collect.c

Collects read subrequest results, unlocks folios, handles EOF/short reads, and triggers retries.

Key behavior:
- Processes only the front of the read stream, preserving ordered completion semantics.
- Clears unread tails on EOF or explicit clear-tail cases.
- For buffered reads, marks folios uptodate, restores/removes private metadata, optionally marks copy-to-cache, and unlocks folios once fully covered.
- Cache read failures become retryable; server download failures become permanent request failures.
- Short reads without EOF/clear-tail/retry progress become `-ENODATA`.
- Completion handles DIO/unbuffered read dcache flushing, kiocb completion, inode dirtying for single-object cache population, task I/O accounting, abandoned page unlocks, and deprecated pgpriv2 cache-copy finalization.
- Exports progress and termination callbacks used by filesystems/cache backends.

Important flags:
- Uses request pause/in-progress flags and subrequest failed/retry/progress/copy-to-cache flags to coordinate retry and collection.
