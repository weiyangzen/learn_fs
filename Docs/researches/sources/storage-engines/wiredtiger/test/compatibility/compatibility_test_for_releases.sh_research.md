# sources/storage-engines/wiredtiger/test/compatibility/compatibility_test_for_releases.sh

Purpose: Legacy shell orchestrator for WiredTiger release compatibility testing across branch pairs, including import compatibility, format verification, checkpoint verification, patch-version upgrade/downgrade, dirty restart, standalone release, and pair-coverage self-test modes.

Important APIs/types/functions: version helpers parse `mongodb-X.Y`; `build_branch` clones/checks out a branch/tag, chooses CMake or autoconf, applies toolchain/preset choices, and builds required artifacts. `create_configs`, `run_format`, `run_test_checkpoint`, `verify_test_format`, `verify_test_checkpoint`, `upgrade_downgrade`, `test_dirty_restart`, `test_upgrade_to_branch`, and `import_compatibility_test` implement the main test phases. `generate_compat_pairs` builds policy-driven branch pairs and `run_pair_tests` validates invariants without builds.

Control flow: command-line flags select exactly one mode. The script creates `test-compatibility-run`, sources `meta/versions.sh`, builds relevant branches, creates format configs, generates data with format/checkpoint tests, verifies backward and forward compatibility, and optionally alternates format binaries for upgrade/downgrade. Newer-branch mode uses generated version-aware pairs for format and upgrade/downgrade, while checkpoint tests still walk the configured release chain.

State and persistence: creates clone/build directories named after branches or tags, per-branch format configs, `RUNDIR.*` homes, backups, imported files, and downloaded WT-8395 test data. It also mutates existing run directories during upgrade/downgrade and dirty restart tests.

Dependencies/integration: depends on git tags/branches, external GitHub clones, CMake/autoconf/make, Snappy/reverse-collator/rotn extensions, `wt`, `test/format`, and `test/checkpoint`. It shares release lists with Python compatibility via `meta/versions.sh`.

Risks and test signals: high-risk areas include branch-list drift, shell quoting/path assumptions, destructive cleanup of the run root, reliance on network and tags, and compatibility config keys that older branches reject. Success is signaled by all invoked build/test/verify commands completing under `set -e`; `-T` provides a cheap structural guard for pair generation.
