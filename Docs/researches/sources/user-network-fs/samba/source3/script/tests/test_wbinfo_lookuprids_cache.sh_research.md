# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_lookuprids_cache.sh

Purpose: regression coverage for winbind `LookupRids` cache behavior. It verifies that deleting an NDR cache key for `wbint_LookupRids` does not prevent a subsequent `wbinfo -R` lookup from succeeding.

Important functions and APIs: uses `wbinfo`, `net cache flush`, `tdbdump`, `tdbtool`, Python import `samba.dcerpc.winbind.wbint_LookupRids`, and subunit helpers. It computes the runtime opnum instead of hard-coding it, dumps `winbindd_cache.tdb`, extracts matching `NDR/.../<opnum>/...` keys, escapes spaces as `\20`, deletes one key, then reruns the lookup.

Control flow: flush cache, run first lookup for RIDs `512,12345`, find/delete the generated cache key, run second lookup, and report through `testok`. On delete failure it prints a post-failure dump of NDR keys.

State and persistence: mutates `$LOCK_DIR/winbindd_cache.tdb` by flushing and deleting a selected cache key. It intentionally exercises persistent winbind cache state.

Dependencies and integration: registered as `samba.wbinfo_lookuprids_cache` in `nt4_member:local`. It requires working Samba Python bindings, TDB tooling, and the winbind cache file.

Risks and test signals: key extraction is dependent on tdbdump formatting and the exact `NDR` key schema. The script disables Bash history expansion because cache keys may contain `!`. Passing signal is successful key deletion and successful second `wbinfo -R`.
