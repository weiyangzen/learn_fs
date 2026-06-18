# sources/user-network-fs/samba/source3/script/tests/test_wbinfo_sids2xids_int.py

Purpose: validates consistency between batched SID-to-XID conversion and singular SID/UID/GID conversion APIs across different winbind cache states.

Important functions and APIs: uses `subprocess.check_output`, `samba.common.get_string`, `wbinfo --own-domain`, `wbinfo -n DOMAIN/`, `wbinfo --sids-to-unix-ids`, `--sid-to-gid`, `--sid-to-uid`, `--uid-to-sid`, `--gid-to-sid`, and `net cache del`. `run()` returns decoded command output. `flush_cache()` deletes IDMAP cache keys. `fill_cache()` primes reverse caches. `check_singular()` compares batched results with singular lookups. `check_multiple()` verifies batched type classifications after cache priming.

Control flow: derive the local domain SID, build a mix of domain, builtin, world, creator, and authentication authority SIDs, flush their cache entries, run the batched conversion, parse id types and numeric IDs, then perform four rounds: singular checks with existing batch cache, singular checks after SID and XID cache flushes, batched checks after UID-to-SID cache fill, and batched checks after GID-to-SID cache fill. It flushes cache entries before exit.

State and persistence: deliberately deletes and primes winbind IDMAP cache keys. No filesystem artifacts are created.

Dependencies and integration: called by `test_wbinfo_sids2xids.sh` and requires Samba Python modules plus working `wbinfo`/`net`. It assumes the output format of `--sids-to-unix-ids` has the ID type at field index 2.

Risks and test signals: `flush_cache()` uses `os.system()` with command strings, so unusual command paths or SID strings could be problematic; in selftest inputs are controlled. Failure exits immediately after printing expected/got details and attempts cleanup.
