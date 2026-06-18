# sources/sync-backup/restic/internal/backend/azure/config.go

Purpose: Defines Azure backend configuration parsing and environment application.

Important APIs and types: `Config` stores account name/key/SAS, credential mode, endpoint suffix, container, prefix, connection limit, and access tier. `NewConfig` supplies defaults. `ParseConfig` parses `azure:container:/prefix`. `ApplyEnvironment` fills missing credential fields from environment variables.

Control flow and state: Parsing validates the `azure:` prefix and requires a colon separating container from path. It cleans and trims the prefix. Environment application only overwrites empty fields and parses `AZURE_FORCE_CLI_CREDENTIAL` as a boolean when present.

Dependencies and integration: Uses `options.Register`, `options.SecretString`, `backend.ApplyEnvironmenter`, `os.Getenv`, and path cleaning. The parsed config feeds `azure.open` and factory registration.

Risks and test signals: Risks include ambiguous container/path separators, silently ignored invalid boolean environment values, and missing validation for access-tier names until open-time matching. `config_test.go` covers valid parse cases.
