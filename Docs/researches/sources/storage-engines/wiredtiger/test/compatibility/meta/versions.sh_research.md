# sources/storage-engines/wiredtiger/test/compatibility/meta/versions.sh

Purpose: Single source of truth for release branch sets used by both shell and Python compatibility tests.

Important APIs/types/functions: exports `SUITE_RELEASE_BRANCHES`, `IMPORT_RELEASE_BRANCHES`, `NEWER_RELEASE_BRANCHES`, `PATCH_VERSION_UPGRADE_DOWNGRADE_RELEASE_BRANCHES`, `TEST_CHECKPOINT_RELEASE_BRANCHES`, and `UPGRADE_TO_LATEST_UPGRADE_DOWNGRADE_RELEASE_BRANCHES`.

Control flow: no execution beyond environment-variable exports. Maintainers add new branches to every relevant list in newer-to-older order and run the shell pair self-test after changing `NEWER_RELEASE_BRANCHES`.

State and persistence: persistent branch policy lives in the exported strings; consumers expand them into arrays or `WTVersion` objects.

Dependencies/integration: sourced by `compatibility_test_for_releases.sh` and parsed by `compatibility_config.py`.

Risks and test signals: missing a branch in one list can silently reduce coverage for a mode. Order matters for sequential checkpoint verification and upgrade paths. The `compatibility_test_for_releases.sh -T` self-test is the explicit signal for pair-policy validity.
