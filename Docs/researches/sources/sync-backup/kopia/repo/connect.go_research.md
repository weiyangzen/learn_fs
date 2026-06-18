# sources/sync-backup/kopia/repo/connect.go

Purpose: connects a local Kopia config file to an initialized repository storage, persists storage/client/cache settings, verifies the connection, and supports disconnecting and client-option updates.

Important APIs/types/functions: `ConnectOptions` embeds `ClientOptions` and `content.CachingOptions`; `ErrRepositoryNotInitialized`; functions `Connect`, `verifyConnect`, `Disconnect`, and `SetClientOptions`.

Control flow: `Connect` reads the repository format blob from storage, maps missing blob to `ErrRepositoryNotInitialized`, parses format JSON, captures storage connection info, applies default client options, sets up cache options using repository unique ID, writes local config, then opens and closes the repository to verify password/config. Verification failure triggers `Disconnect` cleanup. `Disconnect` loads config, removes absolute cache directory and maintenance lock, then removes the config file.

State and persistence behavior: writes and deletes the local config file, cache directory, and maintenance lock path. It never initializes repository storage; it requires the format blob to exist.

Dependencies/integration: integrates blob storage, format parsing, local config serialization, repo open/close, cache option setup, and OS file removal.

Risks and edge cases: `Disconnect` refuses to delete relative cache directories to avoid unsafe removal. A failed verification can remove a just-written config and cache. Password verification depends on `Open`.

Test signals: covered through repository connect/open tests elsewhere; direct tests should cover missing format blob, malformed format JSON, failed verify cleanup, and relative-cache refusal.
