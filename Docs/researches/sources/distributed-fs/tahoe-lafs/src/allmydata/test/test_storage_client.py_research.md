# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_client.py

## Purpose
This file tests Tahoe-LAFS client-side storage discovery and server-selection behavior. It covers native storage server announcement parsing, plugin matching, Foolscap storage adapters, plugin web resources, static server configuration, introducer-driven broker updates, HTTP-over-Foolscap upgrade selection, connection threshold notifications, and the helper that races multiple HTTP NURLs and chooses the first successful endpoint.

## Important APIs, Types, And Helpers
The main production APIs are `NativeStorageServer`, `HTTPNativeStorageServer`, `StorageFarmBroker`, `StorageClientConfig`, `_FoolscapStorage`, `_NullStorage`, `_pick_a_http_server`, `IFoolscapStorageServer`, `IStorageServer`, `IConnectionStatus`, `ANONYMOUS_STORAGE_NURLS`, and `MissingPlugin`. Test helpers include `NativeStorageServerWithVersion`, `new_tub`, `make_broker`, `SpyEndpoint`, and `SpyHandler`.

The test classes are `TestNativeStorageServer`, `GetConnectionStatus`, `UnrecognizedAnnouncement`, `PluginMatchedAnnouncement`, `FoolscapStorageServers`, `StoragePluginWebPresence`, `TestStorageFarmBroker`, and `PickHTTPServerTests`. Fixtures such as `UseNode`, `UseTestPlugins`, `MemoryIntroducerClient`, `SameProcessStreamEndpointAssigner`, `TempDir`, and `WebishServer` provide an in-process node, introducer, web server, and test storage plugin environment.

## Control Flow
The announcement tests instantiate `NativeStorageServer` with modern, old, missing, unrecognized, and plugin-shaped announcements. They call connection lifecycle methods (`start_connecting`, `stop_connecting`, `try_to_connect`) and accessor methods to ensure unsupported announcements degrade to `_NullStorage` or raise `MissingPlugin` only when explicit plugin configuration requires it.

Plugin tests create a node with a configured dummy storage plugin, publish storage announcements to the node's introducer subscription, and inspect the `StorageFarmBroker.servers` entry. Matching announcements produce a plugin-backed storage client that verifies `IFoolscapStorageServer` and receives the expected configuration and announcement. Non-enabled plugin names are ignored.

Storage broker tests configure static servers from YAML, simulate duplicate introducer announcements, verify permutation seed derivation from explicit base32 values, server public-key-like identifiers, or hashed server ids, and test service replacement when an initially Foolscap-only announcement is updated with HTTP NURLs and `force_foolscap = False`. The connection-threshold test uses fake Foolscap `Tub`s and `SpyHandler` endpoints to observe connection attempts, then injects `LocalWrapper(StorageServer(...))` references until `when_connected_enough(5)` fires.

`PickHTTPServerTests` provides a fake `Clock` and request function whose Deferreds fire after configured delays. `_pick_a_http_server` is expected to ignore early failures, return the first successful URL, or raise `MultiFailure` containing all reasons when every candidate fails.

## State And Persistence Behavior
Most tests use temporary node directories containing `private/` and generated node configuration. Static server configuration is loaded from YAML into the broker and persists in broker memory as `_static_server_ids` and `servers`. Plugin web-resource tests exercise persistent in-memory plugin resource state across HTTP requests by checking a counter increases on repeated calls to `/storage-plugins/<plugin>/counter`.

Broker state is Twisted service state. Tests assert old services are running and parented to the broker, then become stopped and unparented when replaced by `HTTPNativeStorageServer`. The connection-threshold test keeps mutable lists of pending fake `Tub`s and observed connection attempts to model asynchronous Foolscap connection establishment.

## Dependencies And Integration Points
The file depends on Foolscap `Tub`, connection hint handlers, Twisted `Service`, Deferreds, Trial, `FilePath`, `Clock`, `hyperlink.URL`/`DecodedURL`, testtools matchers, attrs, and zope interface verification. It integrates with Tahoe node configuration (`config_from_string`, `EMPTY_CLIENT_CONFIG`), introducer subscription handling, web resources, storage plugin loading, storage server wrappers, and HTTP NURL announcement keys.

The plugin tests are an important integration point between the introducer announcement schema (`storage-options`) and plugin-provided `IFoolscapStoragePlugin` clients. The HTTP upgrade test is an integration point between storage-client policy and the newer HTTP storage protocol advertisement key.

## Risks And Edge Cases
Covered risks include old servers lacking `available-space`, announcements missing nicknames, entirely unrecognized announcements, configured-but-missing plugins, plugin name mismatches, plugin resources losing state between requests, duplicate static/introducer server ids, incorrect permutation seed derivation, stale Foolscap services after HTTP upgrade, connection thresholds firing too early, and losing failure reasons when all HTTP NURLs fail.

Residual risk is mostly around simulated networking. Foolscap negotiation is skipped by directly injecting a local reference, so these tests verify broker orchestration and state transitions rather than full network handshakes. The hard-coded Tub certificate improves performance but means certificate-generation behavior is not exercised here.

## Test Signals
Passing this file signals that storage discovery remains backward-compatible, plugin matching is explicit and safe, static server declarations override duplicate introducer announcements, HTTP storage announcements are preferred when allowed, connection waiters are notified only after enough usable servers connect, and multi-NURL HTTP selection reports useful aggregate failures.
