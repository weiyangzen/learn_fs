# sources/sync-backup/kopia/repo/blob/b2/b2_options.go

Purpose: defines persistent JSON options for the deprecated Backblaze B2 storage provider.

Important APIs/types/functions: `Options` with bucket name, prefix, key ID, application key, and throttling limits. The file is behind `!no_extra_providers`.

Control flow: no functions are defined here; validation and client setup happen in `b2_storage.go`. JSON tags define repository config serialization and the key is marked sensitive.

State and persistence behavior: option values are stored through `blob.ConnectionInfo`. Credentials authorize access to a B2 bucket and prefix but this file does not mutate provider state.

Dependencies/integration points: consumed by B2 storage creation and config round-tripping. Risks include provider deprecation, backward compatibility of JSON field names, and no point-in-time or retention options. Live tests cover required bucket/credentials and invalid cases when environment variables are present.
