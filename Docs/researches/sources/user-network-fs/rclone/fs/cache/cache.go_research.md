# sources/user-network-fs/rclone/fs/cache/cache.go

Purpose: implements the process-wide cache of `fs.Fs` backend instances, with canonicalization, expiration, finalizer shutdown, pinning, and special treatment for paths that resolve to files.

Important APIs/types/functions: package-level state includes `once`, cache `c`, mutex `mu`, `remap`, and `childParentMap`. Public functions include `Canonicalize`, `GetFn`, `Get`, `GetArr`, `PutErr`, `Put`, `Pin`, `PinUntilFinalized`, `Unpin`, `ClearConfig`, `Clear`, `Entries`, `ClearMappings`, `ClearMappingsPrefix`, and `EntriesWithPinCount`. Internal helpers include `createOnFirstUse`, `addMapping`, `addChild`, `isChild`, and `getError`. Job hooks `JobGetJobID` and `JobOnFinish` allow rc jobs to pin remotes until completion.

Control flow: on first use, `createOnFirstUse` creates a `lib/cache.Cache`, applies expiration settings from global config, and installs a finalizer that calls backend `Shutdown` when supported. `GetFn` canonicalizes the requested string, calls cache `Get` with a create function using the original string, and stores successful results or `ErrorIsFile` parents. When a newly created backend reports a canonical string different from the lookup key, directories are renamed in cache and mapped; files are renamed to the parent backend, stored without error, and the child path is recorded so later child lookups return `fs.ErrorIsFile`. `Get` copies config/filter settings into a detached background context before calling `fs.NewFs`, then pins for active rc jobs.

State and persistence behavior: cache entries are in-memory only and expire per config. `remap` maps user-supplied strings to canonical cache keys. `childParentMap` tracks file-child to parent relationships so the same cached parent can report file-vs-directory errors based on the original lookup. `ClearConfig` deletes entries and mappings for a config prefix; `Clear` resets cache and mappings.

Dependencies and integration points: depends on `fs`, `filter`, `lib/cache`, `context`, `runtime`, and backend `Shutdowner`. It is a central integration point for all remote creation through `cache.Get`, rc jobs, and config edits that call `ClearConfig`.

Risks: global mutable maps and cache require correct locking; `Canonicalize` and child tracking determine whether callers see `ErrorIsFile`. `ClearMappingsPrefix` counts deletions across two maps and deletes based on mapped parent prefix, so prefix collisions could matter. Long-lived backends intentionally detach from request cancellation, which is correct for reuse but can surprise code expecting context cancellation to close remotes.

Test signals: `cache_test.go` covers cache hits, file-child handling, canonicalization, errors, put/puterr, pin/unpin counts, clear operations, and entries.
