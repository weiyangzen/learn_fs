# sources/sync-backup/kopia/internal/server/api_repo.go

Purpose: implements repository lifecycle and configuration APIs: status, create, exists, connect, disconnect, algorithms, throttle, sync, and description updates.

Important APIs/types/functions: `handleRepoStatus`, `maybeDecodeToken`, `handleRepoCreate`, `handleRepoExists`, `handleRepoConnect`, `handleRepoSetDescription`, `handleRepoSupportedAlgorithms`, `toAlgorithmInfo`, `sortAlgorithms`, throttle handlers, `getConnectOptions`, `connectAPIServerAndOpen`, `connectAndOpen`, `handleRepoDisconnect`, `Server.disconnect`, `handleRepoSync`, and `repoErrorToAPIError`.

Control flow: create/connect decode requests and optional tokens, open blob storage or API-server connections, initialize/open repositories asynchronously when needed, set default policy/maintenance params on create, and install the repository into server state. Status branches direct versus remote repository details. Sync refreshes repository/source state, disconnect closes active state, algorithms returns sorted supported algorithm metadata, and throttle handlers read/write direct repository throttler limits.

State and persistence behavior: creates repository format blobs, writes config/client options, default policies, maintenance params, throttle settings, and mutates server repository/source/scheduler state through `SetRepository`.

Dependencies and integration points: core bridge between `serverapi`, `repo`, `blob`, `policy`, `maintenance`, compression/encryption/hash/splitter packages, and password persistence.

Risks and test signals: async connect can return before completion, token decoding overrides storage/password, and direct-only operations must reject remote repositories. Tests should cover error mapping, already-connected guards, create defaults, disconnect cleanup, and throttle persistence.
