# sources/user-network-fs/samba/source3/passdb/login_cache.c

Purpose: stores a local TDB cache of selected `struct samu` logon state, mainly bad password counters/timestamps and account-control flags.

Important APIs and flow: `login_cache_init()` lazily opens `cache_path("login_cache.tdb")`; `login_cache_shutdown()` closes it. `login_cache_read()` fetches by `pdb_get_nt_username()`, unpacks `SAM_CACHE_FORMAT` (`dwwd`) into timestamp, 16-bit acct flags, bad count, and bad time. `login_cache_write()` packs current timestamp and entry data and stores it by username. `login_cache_delentry()` deletes by username.

State and persistence: static `TDB_CONTEXT *cache` is process-global. Durable cache is `login_cache.tdb` under Samba cache path, mode 0644. Packed timestamps are 32-bit, then cast to `time_t`.

Dependencies and integration: passdb `struct samu` accessors, util_tdb pack/unpack helpers, TDB logging/opening, Samba allocation wrappers.

Risks: `login_cache_shutdown()` does not set `cache` to NULL after successful close, which can leave a stale pointer if the same process tries to reinitialize. The on-disk format stores account-control as 16-bit and times as 32-bit for compatibility, limiting future range/flag expansion. Usernames are used as raw keys, so rename/case behavior depends on passdb conventions.

Test signals: read missing entry, write/read/delete cycle, shutdown/reinit behavior, 64-bit `time_t` compatibility, malformed TDB record handling, and null/empty username cases.
