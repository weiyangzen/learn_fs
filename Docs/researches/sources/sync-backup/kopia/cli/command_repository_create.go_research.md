<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create.go -->
# sources/sync-backup/kopia/cli/command_repository_create.go

Purpose: implements `repository create`, initializing a new repository in a storage provider, optionally connecting to it, setting default policy, and default maintenance parameters.

Important APIs/types/functions: `commandRepositoryCreate`, `newRepositoryOptionsFromFlags`, `ensureEmpty`, `runCreateCommandWithStorage`, `populateRepository`, `repo.Initialize`, `repo.Open`, `repo.WriteSession`, `policy.SetPolicy`, and `setDefaultMaintenanceParameters`.

Control flow: setup registers content format, encryption, ECC, splitter, format version, retention, create-only, key-derivation, shared connect flags, and provider subcommands. Creation verifies storage is empty, obtains a password, builds `repo.NewRepositoryOptions`, initializes storage, optionally connects with the same password, opens the repository, writes default global policy and maintenance parameters, and prints validation guidance.

State/persistence behavior: writes the repository format blob and initial repository contents to blob storage; when not create-only it also writes local config and password persistence.

Dependencies/integration: depends on registered hash/encryption/ECC/splitter algorithms, blob storage listing, repository initialization, policy defaults, and maintenance setup. Risks/test signals: `ensureEmpty` treats any listed blob as existing data and stops before initialization, protecting against accidental overwrite.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create.go -->
