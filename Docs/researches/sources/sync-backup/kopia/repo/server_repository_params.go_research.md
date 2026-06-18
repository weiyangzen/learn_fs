# sources/sync-backup/kopia/repo/server_repository_params.go

Purpose: stores immutable parameters shared by server-backed repository clients.

Important APIs/types/functions: `immutableServerRepositoryParameters` holds hash function, object format, client options, metrics registry, content cache, before-flush callbacks, and `refCountedCloser`. Methods `Metrics` and `ClientOptions` expose registry and client settings.

Control flow: simple getters; setup happens in `openAPIServer` and remote repository code.

State and persistence behavior: in-memory immutable session state. `contentCache` points to a persistent encrypted cache, but this struct only references it.

Dependencies/integration: depends on `cache.PersistentCache`, `metrics.Registry`, `format.ObjectFormat`, `hashing.HashFunc`, and repository callbacks. It embeds `refCountedCloser` for shared cleanup.

Risks: fields are not protected against mutation by referenced objects; callers should treat the struct as immutable by convention. Close lifetime is shared with remote repository clients.

Test signals: API server write-session test indirectly exercises before-flush callbacks and close behavior.
