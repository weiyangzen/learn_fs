# sources/user-network-fs/samba/source3/script/tests/test_winbind_cache_sanity.sh

Purpose: sanity-checks the structural contents of `winbindd_cache.tdb` after a simple name lookup, including cache version, sequence number, and an NDR cache entry.

Important functions and APIs: uses `tdbtool`, `dbwrap_tool`, `wbinfo`, Python `samba.dcerpc.winbind.wbint_LookupName.opnum()`, and subunit helpers. It tests cache readability, performs `wbinfo -n DOMAIN<separator>` to populate cache, fetches `WINBINDD_CACHE_VERSION` as a uint32, checks `SEQNUM/DOMAIN`, and checks the raw NDR key with `tdbtool`.

Control flow: the script validates cache file presence, fills it with a lookup, verifies version key via dbwrap and tdbtool, compares version with `2`, verifies sequence-number key existence, then constructs a byte-escaped NDR key for LookupName and confirms it has the expected data size.

State and persistence: reads and populates the supplied winbind cache file. It does not delete cache entries.

Dependencies and integration: registered in `selftest/tests.py` as `samba3.winbind_cache_sanity` for `ad_member:local`. It depends on the TDB key layout and Samba Python opnum provider.

Risks and test signals: raw NDR key construction is very format-sensitive and domain-length-sensitive; the script currently embeds length bytes for the selftest domain shape. Good signals are successful dbwrap/tdbtool probes and cache version equality.
