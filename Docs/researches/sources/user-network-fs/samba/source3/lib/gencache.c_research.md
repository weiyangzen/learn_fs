# sources/user-network-fs/samba/source3/lib/gencache.c

Purpose: implements a persistent, process-shared generic cache backed by `gencache.tdb`.

Important APIs/types/functions: string/blob set/get/delete/parse/iterate functions, `gencache_timeout_expired()`, `gencache_init()`, `gencache_pull_timeout()`, and expired-entry pruning helpers.

Control flow: initialization opens the lock-directory cache or a per-user fallback. Set locks the key chain, prunes expired entries, and stores timeout+payload+CRC. Get validates CRC and timeout, marks expired records with timeout 0, and returns data. Iterators traverse, validate, pattern-match, and callback.

State/persistence behavior: records are NUL-terminated keys with raw `time_t`, payload, and CRC32. Static `cache` is process-global. Corruption can delete one record or wipe the cache.

Dependencies/integration: used by idmap, name-map, WINS, and utility caches. Depends on TDB wrap, zlib CRC, path helpers, and loadparm.

Risks/test signals: `time_t` ABI, broad wipe-on-corruption, expiration markers, and string/blob NUL handling are risks. Local gencache torture tests cover core paths.
