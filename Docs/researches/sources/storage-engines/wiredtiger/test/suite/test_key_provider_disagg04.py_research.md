# sources/storage-engines/wiredtiger/test/suite/test_key_provider_disagg04.py

Purpose: verifies data remains readable while toggling key-provider extension behavior between version 0 pull mode and version 1 push mode across restarts.

Important APIs and functions: scenarios start at version 0 or 1. `conn_extensions` loads the test key-provider with `version={current_version}`. `checkpoint` conditionally pushes a `CryptKeys` entry and advances stable timestamp for version 1, or just checkpoints for version 0. `restart_with_version` calls `restart_without_local_files`.

Control flow: the test skips non-PALite storage, sets a starting version, reopens, populates batch 1 and checkpoints, restarts with the other version and verifies, adds batch 2 and checkpoints, restarts back to the start version and verifies, adds batch 3 and checkpoints, then restarts to the other version and verifies all data.

State and persistence behavior: persisted layered data encrypted under keys from both provider modes must remain readable after local-file-less restarts. Push-mode checkpoints require stable timestamp advancement to persist pushed keys.

Dependencies and integration points: integrates disaggregated restart semantics, key-provider extension version toggles, layered table data, `CryptKeys`, checkpoint, and dataset validation.

Risks and edge cases: only PALite is covered. `current_version` is mutable class/test state and must be set before connection opens for extension config correctness.

Test signals: each `SimpleDataSet.check()` succeeds after every version flip and after additional writes.
