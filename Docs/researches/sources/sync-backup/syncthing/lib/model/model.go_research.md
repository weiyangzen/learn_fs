# sources/sync-backup/syncthing/lib/model/model.go

## Purpose

`model.go` defines Syncthing's central model service: the long-lived coordinator that binds configuration, folder runners, database index state, protocol connections, request handling, progress tracking, pending device/folder observation, cluster configuration exchange, scans, ignores, versioning, and user-facing query APIs. It implements `Model`, `connections.Model`, `protocol.Model` callbacks, and `config.Verifier`/committer behavior through `CommitConfiguration`.

The file is the integration layer between the BEP protocol layer and folder services. It does little direct file synchronization itself; instead it routes protocol events into `indexHandlerRegistry`, folder runner services, `db.DB`, `ProgressEmitter`, and config mutation helpers.

## Important APIs, Types, and Functions

- `service` is the local folder runner contract. Folder implementations must be suture services and expose scan, pull queue, override/revert, state, error, and statistics operations.
- `Model` is the public model facade used by APIs and other services. It includes scanning, folder state, ignore management, version restore, DB iteration/counts, completion, connection stats, pending device/folder operations, directory tree generation, and outbound block requests.
- `model` owns constructor dependencies (`config.Wrapper`, local `protocol.DeviceID`, `db.DB`, event logger, key generator), concurrency primitives, semaphores, folder maps, connection maps, remote state, device download state, index handlers, and testing counters.
- `NewModel` initializes maps, semaphores, the progress emitter, observed DB, per-device statistics, request limiters, and suture child services.
- `serve` subscribes to config, starts folders with `initFolders`, closes all connections on exit, and handles fatal errors plus deferred connection promotion.
- Folder lifecycle functions include `initFolders`, `newFolder`, `addAndStartFolderLocked`, `restartFolder`, `removeFolder`, and `cleanupFolderLocked`.
- Protocol inbound handlers include `Index`, `IndexUpdate`, `ClusterConfig`, `Closed`, `Request`, `DownloadProgress`, and `OnHello`.
- Config exchange helpers include `generateClusterConfig`, `ccHandleFolders`, `ccCheckEncryption`, `handleIntroductions`, `handleDeintroductions`, `handleAutoAccepts`, and `sendClusterConfig`.
- User/API read methods include `ConnectionStats`, `DeviceStatistics`, `FolderStatistics`, `Completion`, `NeedFolderFiles`, `RemoteNeedFolderFiles`, `LocalChangedFolderFiles`, `GlobalDirectoryTree`, `Availability`, and DB pass-through iterators/counts.
- State mutation APIs include `ScanFolders`, `ScanFolderSubdirs`, `SetIgnores`, `Override`, `Revert`, `BringToFront`, `ResetFolder`, `DismissPendingDevice`, and `DismissPendingFolder`.
- Helper types include `FolderCompletion`, `ConnectionStats`, `ConnectionInfo`, `TreeEntry`, `folderDeviceSet`, `syncMutexMap`, `deviceIDSet`, `storedEncryptionToken`, `updatedPendingFolder`, and `redactedError`.

## Control Flow

Startup flows through `NewModel` into suture children and `serve`. `serve` subscribes the model as a config committer, initializes all unpaused folders, cleans stale pending records, sends initial cluster configs, then waits for context cancellation, fatal errors, or the promotion timer. On shutdown, `closeAllConnectionsAndWait` closes every active protocol connection and waits on per-connection closed channels.

Folder startup creates ignore matchers, drops stale DB device indexes for devices no longer shared with the folder, creates roots/markers for blank folders, loads receive-encrypted tokens, hides Syncthing metadata paths, constructs versioners, warns about protected files, creates a runner via `folderFactories`, and registers the runner with index handlers. Restart is serialized per folder by `folderRestartMuts` so concurrent config commits do not leave duplicate runners alive.

Inbound index flow validates that the announced folder exists, is shared with the sending device, and is not paused. It then locates the index handler for the connection and delegates full or incremental updates to `ReceiveIndex`, preserving BEP sequence metadata.

Inbound cluster config flow is more involved. `ClusterConfig` ignores secondary configs, ensures an index handler for the primary connection, validates that the remote and local device entries exist for every announced folder, optionally auto-accepts folders by modifying config and waiting for the commit, processes folder sharing/encryption/pending state in `ccHandleFolders`, records remote folder states, subscribes temporary indexes through `ProgressEmitter`, and applies introducer/deintroducer config mutations when the peer is configured as an introducer.

Connection flow starts with `OnHello` for unknown-device observation and `AddConnection` for known devices. `AddConnection` stores the connection by ID, appends it to the device's ordered connection slice, logs events, maybe adopts the remote device name, updates last-seen stats, and schedules promotion. `promoteConnections` chooses the first connection as primary for each device, sends a full cluster config to primaries, starts secondaries, and sends a secondary-marked cluster config. `Closed` removes connection state, unsubscribes temporary indexes for removed primaries, tears down index handlers when necessary, schedules promotion, updates device stats, emits disconnect events, and closes the connection's wait channel.

Inbound request flow validates nonnegative sizes/offsets, folder existence, sharing, pause state, canonical filename, internal-file rejection, ignore rejection, request semaphores, symlink traversal, optional temporary file reads, regular-file checks, read errors, and content hash validation. Hash mismatch on a normal folder schedules `recheckFile` to force-rescan a file that DB metadata says should have matched but disk bytes did not.

Config commit flow waits for startup, adds new folders, removes missing folders, restarts folders when restart-only settings or ignore cache behavior changed, emits pause/resume events, creates stats refs for new devices, closes connections for paused/removed devices, updates per-device request limiters, sends cluster configs to affected devices, cleans pending records, resizes global/folder semaphores, and returns whether no external restart is needed.

## State and Persistence Behavior

The central mutable state is guarded by `m.mut`. It includes folder configs, ignore matchers, folder runners, versioners, encryption password tokens/failures, live connections, per-device connection ordering, promoted connection IDs, request limiters, hello messages, device download states, remote folder states, and index handlers. Folder restarts also use a per-folder mutex stored in `syncMutexMap`.

Persistence is delegated primarily to `db.DB`, typed stats DB references, and `db.ObservedDB`. The model reads and writes local/remote file indexes, folder/device counts, sequences, block-hash lookup metadata, observed pending devices, observed pending folders, and per-device statistics. Folder removal drops folder DB state, while reset drops metadata only when the folder is paused. Unknown device/folder offers are persisted as pending observations and reconciled by `cleanPending`.

Receive-encrypted folder state persists an encryption token as JSON under the folder marker path (`MarkerName/EncryptionTokenName`). `ccCheckEncryption` loads or writes that token and caches it in memory. Path-related errors are wrapped in `redactedError` to keep sensitive paths out of public failure events.

Request limiting state uses semaphores. `newLimitedRequestResponse` takes bytes from per-device and global semaphores and returns them only when the protocol response is closed, so callers must close responses to avoid capacity leaks.

## Dependencies and Integration Points

`model.go` integrates with:

- `suture` and `svcutil` for service supervision.
- `config.Wrapper` for config subscriptions, defaults, validation, and mutation waits.
- `db.DB` and `db.ObservedDB` for file index, counts, stats, pending offers, and metadata persistence.
- `protocol.Connection`, BEP message structs, device IDs, vectors, and request/response types.
- Folder runner implementations registered in `folderFactories`.
- `ignore.Matcher`, `fs.Filesystem`, `osutil`, and `scanner` for path, ignore, symlink, read, and hash behavior.
- `events.Logger` for device, folder, download, cluster-config, pending, and failure events.
- `ProgressEmitter` for temporary index subscriptions and active pull progress.
- `versioner` for file versions and restore operations.
- `stats` for device/folder statistics.
- `semaphore` for global incoming request limits, per-device request limits, and folder I/O concurrency.

## Risks and Edge Cases

- Lock ordering matters. Some methods intentionally collect post-lock actions or wait outside `m.mut` to avoid deadlocks with folder shutdown or protocol connection callbacks.
- `folderCompletion` assumes `m.deviceDownloads[device]` exists for queried devices; most connected/known-device paths populate it, but unusual direct calls can be sensitive to nil map entries.
- Request responses must be closed by consumers. Capacity in request semaphores and buffers in `protocol.BufferPool` are released on `Close`.
- `CommitConfiguration` uses `reflect.DeepEqual` on restart-only config projections. Incorrect projections can either miss required restarts or restart too often.
- Auto-accept creates directories and writes default ignores while processing cluster configs; races are mitigated by config waiter synchronization but still carry filesystem and path-conflict risks.
- Receive-encrypted handshake is token-sensitive. Mismatched local/remote token direction returns distinct errors, and read/write failures are deliberately redacted.
- `GlobalDirectoryTree` assumes database directory entries precede child entries enough to build parents; malformed or unsorted metadata can produce parent lookup errors.
- Connection promotion depends on ordered `deviceConnIDs`, with index handling tied to the primary connection.

## Test Signals

`model_test.go` provides extensive coverage for this file. It exercises request validation, index benchmarks, device renaming and persistence, cluster config generation, encrypted cluster config filtering, introducer/deintroducer behavior, auto-accept permutations, ignore load/write behavior, scan recovery, directory tree rendering, folder add/pause/remove restart behavior, unknown-device index cleanup, disconnect cleanup, internal scan edge cases, request limit blocking, connection close on restart, modtime windows, device pause events, folder API errors, rename detection/sequence ordering, block-hash lookup maintenance, cluster config resend triggers, completion math, receive-only deletion accounting, encryption consistency, pending folder cleanup, and receive-only/receive-encrypted deletion behavior.
