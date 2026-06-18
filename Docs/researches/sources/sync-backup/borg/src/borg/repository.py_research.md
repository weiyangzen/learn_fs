# sources/sync-backup/borg/src/borg/repository.py

Purpose: modern Borg repository abstraction backed by `borgstore`, using namespaced store objects instead of legacy segment journals.

Important APIs/types: `Repository` handles create/open/close/destroy, locks, keys, manifest, object access, checks, chunk index cache, and generic store wrappers. `PackWriter` buffers chunks into pack objects and updates `ChunkIndex`. Helpers map permissions and build REST backends/commands.

Control flow/state: construction resolves URL/location, configures namespaces, maps permissions, and opens either local or REST store. Create writes readme/version/id and an empty chunk index cache. Open validates config and locks. `put` goes through `PackWriter`; current `max_count=1` means pack ID equals chunk ID. `get` resolves chunk index entries and can load full object bytes or header+metadata only. Close persists loaded chunk index incrementally and releases lock/store.

Persistence: `config/`, `keys/`, `archives/`, `packs/`, `cache/`, and `locks/` store repo state. Repokeys are content-addressed by sha256. Manifest is `config/manifest`; packs are `packs/<pack_id_hex>`.

Dependencies/integration: uses `borgstore.Store`, REST backend over `borg serve --rest`, `storelocking.Lock`, `ChunkIndex`, `RepoObj`, keyfile detection, cache helpers, and `Manifest` errors.

Risks: several paths assume N=1 packing, especially delete/list chunk_id-to-pack_id mapping. Pending pack index entries must be cleaned on store failures; `PackWriter` does this. Metadata-only reads must stay pack-boundary-safe for future N>1. Permission maps must match namespace behavior.

Test signals: create/open validation, permission modes, REST command generation, key load/save/delete, lazy chunk index cache, PackWriter failure cleanup, metadata-only get, check/repair checkpoints, and N=1 list/delete semantics.
