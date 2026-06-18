# sources/user-network-fs/samba/source3/torture/test_idmap_cache.c

Purpose: This file tests Samba's local idmap cache for SID-to-unixid and unixid-to-SID lookups, including deletion and negative mapping behavior.

Important APIs/types/functions: The public entrypoint is `run_local_idmap_cache1()`. It uses `dom_sid_parse()`, `dom_sid_equal()`, `idmap_cache_set_sid2unixid()`, `idmap_cache_find_sid2unixid()`, `idmap_cache_find_xid2sid()`, and `idmap_cache_del_sid()`. Data types are `struct dom_sid` and `struct unixid`.

Control flow: The test stores a UID mapping for a concrete domain SID, looks it up by SID and by unixid, verifies the returned type/id and SID, confirms that changing the lookup type to GID does not find the UID mapping, deletes the SID mapping, then verifies the UID lookup is gone. It then stores a negative mapping using the zero SID and verifies that reverse lookup finds the negative result.

State/persistence behavior: The idmap cache is global/local process state backed by Samba cache infrastructure, not by a file created in this test. The `expired` flag is checked on every successful lookup and must be false. Deletion mutates the cache and is verified immediately.

Dependencies and integration points: It depends on `lib/idmap_cache.h`, generated idmap NDR types, and SID helpers. The test is a local cache contract check used by winbind/idmap code paths.

Risks: Cache state from other tests could interfere if the same SID/xid keys are reused, though this test uses a specific SID and deletes it. Negative mapping semantics are easy to regress because a zero SID is a valid cache payload with special meaning.

Test signals: Passing requires successful nonexpired forward and reverse lookups, correct UID/GID discrimination, no stale lookup after deletion, and successful reverse lookup of the negative zero-SID mapping.
