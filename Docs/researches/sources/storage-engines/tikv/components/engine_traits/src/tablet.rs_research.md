# sources/storage-engines/tikv/components/engine_traits/src/tablet.rs

Purpose: Provides tablet abstractions for multi-RocksDB/tablet architecture, including latest-tablet caching and registry management.

Important APIs and control flow: `CachedTablet` wraps shared latest tablet data plus a local cache/version; `set` updates shared state and version, `latest` refreshes stale local cache, and `release` drops cache. `TabletContext` carries region id, suffix, encoded key bounds, and optional flush state. `TabletFactory` opens/destroys/exists-checks tablets. `SingletonFactory` returns one shared tablet for tests. `TabletRegistry` owns a root path, factory, and region-id map, formats/parses tablet names, computes paths, gets/defaults/removes cached tablets, loads tablets with optional creation, and iterates opened tablets releasing local caches.

State, persistence, and dependencies: Registry state is in-memory; tablet data lives under root paths managed by factories. `TabletContext::flush_state` links tablet persistence to apply-index flushing.

Integration points, risks, and test signals: Used by multi-tablet storage engines and recovery. Risks include stale local caches until `latest`, suffix/path naming collisions, loading an already-open tablet, `create=false` existence checks, broad locks during iteration, and factory-specific destroy semantics. Tests cover cache refresh, singleton behavior, registry load/update/remove/path parsing, and memory-tablet duplicate opens.
