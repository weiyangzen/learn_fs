# sources/sync-backup/borg/src/borg/testsuite/archiver/checks_test.py

Purpose: tests security and compatibility checks around repository identity, cache/security metadata, mandatory feature flags, remote extraction behavior, and old cache integrity data.

Important APIs/types/functions: helper `get_security_directory` derives Borg's security directory from repository ID. `add_unknown_feature` injects mandatory feature flags into a manifest. `cmd_raises_unknown_feature` abstracts forked CLI exit versus in-process `MandatoryFeatureUnsupported`. Tests use `Cache`, `Manifest`, `Repository`, `Location`, `get_security_dir`, `bin_to_hex`, and shared file/repo helpers.

Control flow: repository swap tests create an encrypted repository, cache it, replace it with an unencrypted or different repository sharing location/ID characteristics, and assert Borg aborts. No-cache variants delete cache/security state and retest. Blank-passphrase repokey tests ensure encrypted-with-empty-passphrase is treated like plaintext from a warning perspective. Repository move tests require explicit `BORG_RELOCATED_REPO_ACCESS_IS_OK` once, then persist the new location. Unknown unencrypted repository tests require confirmation when cache/security knowledge is gone. Unknown feature tests inject mandatory flags for WRITE, CHECK, READ, DELETE, and mount/rename operations and assert the relevant commands reject unsupported features, except whole-repo delete. Cache mandatory-feature cleanup verifies stale unknown cache features are cleared after a forked create. Remote strip-components extraction asserts no cached remote responses leak.

State and persistence behavior: heavily mutates repositories, cache directories, security directories, manifest feature flags, and environment variables. It also replaces repository directories to simulate attacks or relocations.

Dependencies and integration points: covers Borg cache/security-dir trust model, manifest feature negotiation, command operation classification, remote repository response cache cleanup, and FUSE mount restrictions when llfuse is available.

Risks: tests depend on precise cache/security path layout and environment-variable confirmation names. Direct manifest feature injection must stay aligned with feature flag schema. Remote-only leak detection relies on a debug marker string.

Test signals: strong security regression signals for repository swap/move warnings, unknown feature handling, and remote extraction response draining.
