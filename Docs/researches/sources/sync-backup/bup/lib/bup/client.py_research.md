# sources/sync-backup/bup/lib/bup/client.py

## Purpose
Implements bup's remote repository client and remote pack store. It supports SSH, TCP bup daemon, and reverse/fd transports, command negotiation, index syncing, remote object writes, refs, object reads, rev-list, path resolution, and remote config queries.

## Important APIs, Types, and Functions
Exports `ClientError`, `Config`, `Client`, and `RemotePackStore`. Internal context managers `_TypicalCall` and `_LineBasedCall` synchronize protocol calls. Transport classes are `ViaBupRev`, `ViaSsh`, and `ViaBup`.

## Control Flow
`Client.__init__` opens the selected transport, asks `help` for commands, optionally sets/init-dir, prepares cache by repo id or legacy id, then exposes methods for indexes, pack writing, refs, cat/join, rev-list, resolve, and config-get. `RemotePackStore.write` frames objects with length, SHA, CRC, and data, throttles by `bwlimit`, handles server suggestions, and finishes packs with a zero-length marker.

## State and Persistence Behavior
Persistent local state is the index cache directory and synced `.idx`/midx files. Remote state includes repository refs, objects, packs, and optional config. Runtime state tracks busy protocol command, transport handles, object cache, bandwidth counters, and pack-open state.

## Dependencies and Integration Points
Depends on `git`, `ssh`, `vint`, `protocol`, `PackWriter`, helper connection classes, path index cache, URL parsing, sockets, and zlib. It is the client side of the bup server protocol and must match server command names and framing.

## Risks and Test Signals
Risks include protocol desynchronization on exceptions, stale index cache naming, bandwidth sleep behavior, remote process/socket cleanup, ref/object parsing, and inability to abort remote pack writes. Signals are help negotiation, command availability errors, synced indexes, successful remote pack writes, refs/rev-list equality, resolve errors, and config-get type handling.
