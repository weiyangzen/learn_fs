# sources/distributed-fs/tahoe-lafs/src/allmydata/test/storage_plugin.py

## Purpose
This file implements a dummy storage server/client plugin used by Tahoe-LAFS tests. It validates the storage plugin extension points for server announcement construction, client construction, and plugin-provided web resources.

## Important APIs, Types, And Functions
Important types are `RIDummy`, `DummyStorage`, `GetCounter`, `DummyStorageServer`, and `DummyStorageClient`. `DummyStorage` implements `IFoolscapStoragePlugin`, while `DummyStorageServer` implements `RIDummy` and `DummyStorageClient` implements `IStorageServer` incompletely for tests. It returns `AnnounceableStorageServer` and uses `jsonbytes.dumps`, Twisted `Data`, and `Resource`.

## Control Flow
`DummyStorage.get_storage_server` validates plugin configuration, raises on an `invalid` setting, builds a plugin announcement, and returns a successful Deferred containing an announceable storage server. `get_storage_client` captures plugin configuration and announcements for client-side tests. `get_client_resource` renders plugin config as JSON and adds a dynamic `counter` child whose `render_GET` increments a class-level value.

## State, Persistence, And Dependencies
Plugin state is primarily configuration-derived. `GetCounter.value` persists across instances at class level. The dummy server stores the callback for anonymous storage server access but does not implement real storage behavior.

## Risks And Test Signals
The module intentionally offers just enough interface behavior for plugin integration. It catches whether Tahoe adds plugin announcements, handles plugin errors, produces stable fURLs, and exposes web resources, but it is not a substitute for full storage server compatibility testing.
