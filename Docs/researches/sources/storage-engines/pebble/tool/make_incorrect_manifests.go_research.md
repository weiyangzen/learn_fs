## sources/storage-engines/pebble/tool/make_incorrect_manifests.go

Purpose: build-tagged fixture generator for an intentionally invalid MANIFEST used by manifest check tests.

Important APIs/types/functions: `writeVE` appends and encodes a `manifest.VersionEdit` to a `record.Writer`, fataling on errors. `makeManifest1` creates `tool/testdata/MANIFEST-invalid`, writes two version edits with the LevelDB comparer, min-unflushed log numbers, next file/last sequence metadata, and L6 tables with conflicting sequence ranges. `main` calls `makeManifest1`.

Control flow: guarded by `//go:build make_incorrect_manifests`; it runs only when explicitly invoked with the documented `go run -tags make_incorrect_manifests` command. It overwrites the fixture path using `vfs.Default`.

State and persistence: persists a MANIFEST fixture under `tool/testdata`. The generated edits are crafted to violate manifest/version invariants for negative testing.

Dependencies and integration: uses Pebble internal `manifest`, `record`, `base`, and `vfs`. The output is consumed by datadriven `manifest_check` fixtures through `manifest.go`.

Risks: running from the wrong working directory writes to an unexpected relative path. It uses `log.Fatal`, suitable for a generator but not a library. Any manifest encoding format change requires regenerating fixture expectations.

Test signals: supports tests that ensure `manifest check` reports invalid version application rather than silently accepting corrupt metadata.
