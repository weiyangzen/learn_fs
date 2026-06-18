# sources/sync-backup/borg/src/borg/manifest.py

Purpose: manages manifests, archive listings, and repository feature compatibility for modern and legacy repositories.

Important APIs/types: `Manifest.load` fetches/decrypts manifest data, creates a key if needed, chooses `Archives` or `LegacyArchives`, loads config/timestamp/item keys, and checks mandatory feature flags for requested `Operation`s. `Manifest.write` stores a monotonic-timestamp manifest object. `Archives` manages modern borgstore archive entries. `ArchiveInfo` is the public archive tuple. `filter_archives_by_date` applies relative date filters.

Control flow/state: modern archive IDs come from `repository.store_list("archives")`. Metadata is loaded from repository objects and parsed as `ROBJ_ARCHIVE_META`, with synthetic metadata for missing/corrupt archive objects. Listing applies matching (`aid:`, `tags:`, `user:`, `host:`, name/glob/regex), date filters, sorting, first/last, and reverse. Manifest write serializes `ManifestItem` through `RepoObj` to `MANIFEST_ID`.

Persistence: manifest object is stored via `repository.put_manifest`; modern archive presence is stored as `archives/<hex-id>` entries; feature flags and item keys live in manifest config.

Dependencies/integration: depends on `RepoObj`, key factory, `ArchiveItem`, `ManifestItem`, patterns, time helpers, borgstore item info, and legacy repository type checks. Security code uses manifest timestamp and key.

Risks: archive listing can be expensive. Corrupt/missing metadata is represented as sentinel entries. Feature flag serialization must stay compatible. Archive ID prefix matching requires exactly one match.

Test signals: load/write round trips, monotonic timestamps, feature rejection, archive create/delete/undelete/nuke, matching/date filters, corrupt metadata sentinels, and legacy archive interface selection.
