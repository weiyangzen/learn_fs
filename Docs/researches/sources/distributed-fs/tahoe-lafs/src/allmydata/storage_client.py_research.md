# sources/distributed-fs/tahoe-lafs/src/allmydata/storage_client.py

## Purpose
Implements the client-side storage broker and storage-server descriptors. It discovers servers from static config and introducer announcements, chooses Foolscap or HTTP transport, tracks connection state, exposes `IServer`/`IStorageServer` objects to upload/download code, handles Grid Manager upload policy, and adapts HTTP storage APIs to legacy Foolscap-style interfaces.

## Important APIs, Types, And Functions
`StorageClientConfig` parses preferred peers, storage plugins, and Grid Manager keys from node config. `StorageFarmBroker` maintains `servers`, static server ids, introducer subscription, connection thresholds, server permutation, static server setup, announcement handling, and server lookup helpers. `_parse_announcement()`, `_make_storage_system()`, `_storage_from_foolscap_plugin()`, and `_available_space_from_version()` build transport-specific descriptors. `NativeStorageServer` manages Foolscap connection/reconnection and version discovery. `HTTPNativeStorageServer` polls HTTP NURLs, selects a working server, and exposes equivalent descriptor metadata. `_StorageServer` is the Foolscap remote-reference pass-through. `_HTTPStorageServer`, `_HTTPBucketWriter`, and `_HTTPBucketReader` adapt HTTP immutable/mutable operations to `IStorageServer`.

## Control Flow
The broker receives static definitions or introducer announcements, ignores announcements shadowed by static config or unchanged from previous state, creates a descriptor, replaces old descriptors when announcements change, and starts connection management. Peer selection filters connected servers, optionally excludes Grid Manager invalid servers for uploads, prioritizes preferred peers, and sorts by permutation seed. Foolscap descriptors connect a Tub to a FURL, fetch version info, retain stale references after loss for existing users, and notify status listeners. HTTP descriptors loop on `_connect()`, pick the first usable NURL with parallel version probes, cache an `_HTTPStorageServer`, and periodically refresh version/liveness.

## State And Persistence
State is in memory: server maps, static id set, high-water connection count, rrefs, reconnectors, status observers, HTTP selected NURL/client, cached version, and connection status. Configuration comes from `tahoe.cfg` and announcement dictionaries. No durable storage is written by this file.

## Dependencies And Integration Points
Integrates with IntroducerClient, Foolscap Tub/RemoteReference/Reconnector, Twisted services and Deferreds, HTTP storage client classes, plugin discovery through Twisted plugins, Grid Manager certificate verification, Tor provider connection handlers, upload peer selection through `permute_server_hash`, Tahoe interfaces, and web resources for enabled storage plugins.

## Risks And Test Signals
Risks include stale or malformed announcements, static/introducer precedence, plugin mismatch reporting, v0 server id parsing, Grid Manager certificate filtering, differences between HTTP and Foolscap error semantics, HTTP polling cancellation, stale rrefs after disconnect, and availability fields from old version dictionaries. Tests should cover static server creation, announcement replacement, preferred peer ordering, upload filtering, threshold callbacks, Foolscap and HTTP `get_storage_server()` lifecycle, NURL failover, mutable/immutable HTTP adapters, 404/401 error mapping, and missing plugin diagnostics.
