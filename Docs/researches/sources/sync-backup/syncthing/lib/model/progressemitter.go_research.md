# sources/sync-backup/syncthing/lib/model/progressemitter.go

## Purpose

`progressemitter.go` implements `ProgressEmitter`, the model subservice that publishes active pull progress locally through `events.DownloadProgress` and remotely through BEP `DownloadProgress` messages. It tracks active `sharedPullerState` instances, periodically detects changes, emits GUI/API event payloads, and advertises temporary block availability to subscribed peer connections.

The emitter is also a config committer. It enables, disables, clears, or retunes itself when progress update interval and temporary index threshold settings change.

## Important APIs, Types, and Functions

- `ProgressEmitter` stores config, active puller registry (`folder -> file -> state`), timer interval, minimum temporary-index block threshold, sent temporary-index state per device, subscribed connections, folders per connection, disabled flag, event logger, mutex, and timer.
- `progressUpdate` bundles a protocol connection, folder ID, and `protocol.FileDownloadProgressUpdate` list. Its `send` method sends a BEP `DownloadProgress` message.
- `NewProgressEmitter` creates maps, initializes the short timer, applies current config with `CommitConfiguration`, and returns a ready service.
- `Serve` subscribes to config and runs the timer loop. On timer ticks, it checks registry count and latest puller update timestamp, emits local events, computes remote updates, resets the timer when work remains, unlocks, then sends network messages outside the mutex.
- `sendDownloadProgressEventLocked` builds the nested event payload of folder/file to `PullerProgress`.
- `computeProgressUpdates` computes per-device, per-folder temporary-index append/forget updates using `sentDownloadState`.
- `CommitConfiguration` enables/disables progress emission, updates interval, updates `minBlocks`, and clears current state when disabled.
- `Register` and `Deregister` add/remove active puller states.
- `BytesCompleted` sums current active pull progress by folder.
- `temporaryIndexSubscribe` and `temporaryIndexUnsubscribe` manage peer subscriptions set up by the model after cluster config exchange.
- `clearLocked` sends cleanup messages for known sent temporary-index states and resets all maps.

## Control Flow

When a puller starts, it calls `Register`. If the registry was empty, the timer is reset so the service wakes up. On each timer tick, `Serve` scans all registered puller states for a newer `Updated` timestamp or a changed registry count. If nothing changed, no event or protocol message is emitted. If something changed, the service sends one local event snapshot and computes remote temporary-index deltas.

Remote update computation iterates subscribed device connections and only considers folders currently subscribed for that device. It filters out puller states for other folders, symlinks, directories, and files whose block count is at or below `minBlocks`. For active regular files above the threshold, it updates per-device `sentDownloadState`, producing append updates for new available blocks and forget updates for vanished or version-changed states. It also drops sent state for disconnected devices and cleans state for folders no longer shared with a device, although forget messages for unshared folders are intentionally not sent in the current code path.

Network sends happen after unlocking. This prevents blocked peer I/O from holding the emitter mutex and delaying puller registration/progress reads, at the cost of remote progress messages being best-effort under back-pressure.

## State and Persistence Behavior

The emitter has no disk persistence. All state is in memory and protected by `mut`. `registry` tracks current active pullers. `sentDownloadStates` remembers what temporary block availability has already been announced to each device so messages can be incremental and cleanup/forget messages can be generated. `connections` and `foldersByConns` mirror temporary-index subscriptions controlled by the model.

Disabling the emitter clears active registry and sent states. `clearLocked` attempts to send cleanup messages before clearing, using `context.Background()`. Since cleanup sends occur while called under the lock, blocked protocol implementations would be more sensitive here than in the normal `Serve` send path.

## Dependencies and Integration Points

`ProgressEmitter` depends on:

- `config.Wrapper` and `config.Configuration` for runtime options.
- `events.Logger` for local `DownloadProgress` events.
- `protocol.Connection`, `protocol.DownloadProgress`, and `protocol.FileDownloadProgressUpdate` for BEP progress messages.
- `sharedPullerState`, `PullerProgress`, and `sentDownloadState` types defined elsewhere in the model package.
- The model's cluster-config handling, which calls `temporaryIndexSubscribe` and `temporaryIndexUnsubscribe` when peers are eligible for temporary indexes.

## Risks and Edge Cases

- Timer behavior depends on registry count. If a puller is registered while disabled, it is ignored; when re-enabled, old ignored states are not resurrected.
- `computeProgressUpdates` iterates maps, so update ordering is intentionally nondeterministic.
- Temporary-index cleanup for folders no longer shared is currently state-only; sending forget updates is commented out because unsharing normally reconnects the peer.
- `clearLocked` performs protocol sends under the mutex, unlike the normal timer path.
- The emitter filters on `len(file.Blocks) <= minBlocks`, so exactly-at-threshold files do not advertise temporary indexes.
- Progress events only emit on observed timestamp/count changes. Puller states must update their timestamps reliably.

## Test Signals

`progressemitter_test.go` validates local event emission for register/progress/deregister changes and no duplicate events when nothing changes. It also validates temporary-index message generation: minimum block threshold, append deltas, no-op unchanged timestamps, version changes producing forget plus append, puller creation timestamp changes, empty append updates, multi-file/multi-folder batching, deletion forget messages only once, inactive puller filtering, folder subscription changes, and state cleanup after unsubscribe.
