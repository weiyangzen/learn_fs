# File Research: sources/os/linux/linux/fs/nfsd/filecache.h

Read completely: 88 lines.

Header for the NFSD open-file cache data structures and public acquisition/lifecycle APIs.

Key responsibilities:
- Defines `NFSD_FILE_GC_BATCH`, limiting how long list_lru locks are held during scans.
- Defines `struct nfsd_file_mark`, the fsnotify mark wrapper with an independent refcount for nfsd_file references.
- Defines `struct nfsd_file`, including rhashtable linkage, inode comparison key, backing file, credential, net namespace, state flags, refcount, access mask, fsnotify mark, LRU/GC lists, RCU head, birth time, and DIO alignment fields.
- Defines state bits for hashed, pending construction, referenced, garbage-collected, and recent entries.
- Declares cache init/shutdown/purge, per-net start/shutdown, reference management, file access, inode close, disposal, cache query, file acquisition variants, and stats output.

Notable risks:
- The comment on `nf_inode` is essential: it is not a live reference.
- API callers must pair each successful acquire/get with `nfsd_file_put`, and LOCALIO callers must also handle the returned net namespace lifetime via `nfsd_file_put_local`.
