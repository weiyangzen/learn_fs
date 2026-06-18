# sources/user-network-fs/rclone/backend/union/union.go

Purpose: main implementation of rclone's union backend, overlaying multiple upstream remotes as one filesystem.

Important APIs: `Fs`; `NewFs`; policy wrappers `action`, `create`, `searchEntries`; operations `Mkdir`, `MkdirMetadata`, `Rmdir`, `Purge`, `Copy`, `Move`, `DirMove`, `DirSetModTime`, `ChangeNotify`, `DirCacheFlush`, `Put`, `PutStream`, `About`, `List`, `ListR`, `NewObject`, `Shutdown`, `CleanUp`; helpers `wrapEntries`, `mergeDirEntries`, `multiReader`, `put`, `multithread`.

Control flow/state: `NewFs` parses options, migrates deprecated remotes, rejects invalid upstream sets, constructs upstream wrappers concurrently, prepares writeback, resolves policies, masks features, computes hash intersections, and returns root-as-file errors when needed. List/ListR fan out, wrap entries, merge by remote path, and apply search policy. Writes use create policy, recursively create parents, tee data to selected upstreams, and aggregate errors.

Dependencies/integration: union `common/policy/upstream`, rclone `fs`, config, `hash`, `operations`, `walk`, plus standard concurrency/io/path packages. Implements many optional rclone interfaces.

Risks/test signals: partial multi-upstream failures, feature masking surprises, stream tee backpressure, stale usage-based policy decisions, and nil entries from mixed metadata support. Tests cover standard, RO, NC, policy variants, read-only fallback, and mixed Move/Copy capability.
