<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go -->
# sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go

Purpose: format-specific integration tests for repository parameter mutation, retention settings, format upgrades, downgrade prevention, required features, and server reaction to new unsupported features.

Important APIs/types/functions: `setupInMemoryRepo`, `TestRepositorySetParameters`, `TestRepositorySetParametersRetention`, `TestRepositorySetParametersUpgrade`, `TestRepositorySetParametersDowngrade`, `TestRepositorySetParametersRequiredFeatures`, and `TestRepositorySetParametersRequiredFeatures_ServerMode`.

Control flow: tests create in-memory repositories, inspect status defaults, check no-op output, validate failure cases, set index/max-pack settings, enable/update/disable retention, upgrade to latest epoch format, set epoch tunables, reject invalid tunables, prevent index downgrades, add/remove unknown required features, and verify a running server exits when it encounters a new required feature.

State/persistence behavior: mutates repository format and retention metadata repeatedly and checks state through `repository status` and `index epoch list`.

Dependencies/integration: spans format versions, in-memory reconnectable storage, maintenance validation, server start, policy scheduling, and required-feature gates. Risks/test signals: server-mode test is timing-sensitive because it waits for scheduled snapshot activity to notice the unsupported feature.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_set_parameters_test.go -->
