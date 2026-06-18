# sources/sync-backup/borg/src/borg/testsuite/archiver/corruption_test.py

Purpose: tests detection of cache integrity metadata modified by older Borg versions that did not maintain the integrity section consistently.

Important APIs/types/functions: `corrupt_archiver` creates test files, initializes a repository, and extracts the cache path from `repo-info --json`. `test_old_version_interfered` uses `ConfigParser` to modify the cache config's main `manifest` value while leaving integrity metadata untouched.

Control flow: after setup, the test skips if no cache path exists for the cache implementation. It edits `<cache>/config`, sets `cache.manifest` to the hex representation of 32 zero bytes, writes the config, then runs `repo-info` and expects a warning that old Borg modified the cache and integrity data is unavailable.

State and persistence behavior: directly modifies the on-disk cache configuration file for the test repository. Repository contents remain valid; only cache metadata is corrupted.

Dependencies and integration points: covers cache config parsing, `repo-info` cache integrity checks, `bin_to_hex`, JSON repo-info output, and the shared archiver harness.

Risks: depends on cache implementation exposing a filesystem `path` and a `config` file with a `[cache] manifest` key. Alternative cache backends skip or need adapted tests.

Test signals: verifies Borg surfaces a clear warning instead of silently trusting mismatched cache integrity data.
