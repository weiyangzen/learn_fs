# Research: sources/sync-backup/syncthing/test/manypeers_test.go

## sources/sync-backup/syncthing/test/manypeers_test.go

Purpose: integration test ensuring a folder can sync when a peer has many configured devices.

Important APIs/functions: `TestManyPeers`, REST `Get("/rest/system/config")`, `Post("/rest/system/config")`, and `rc.AwaitSync`.

Control flow: cleans two-peer state, generates files in `s1`, starts receiver h2, fetches config, appends random device IDs until there are 100 devices and corresponding folder device entries, posts modified config, starts sender h1, resumes both, awaits sync, then compares directories.

State and persistence: temporarily rewrites h2 config, mutates s1/s2 data and indexes.

Dependencies and integration: config JSON marshaling, random device ID generation, REST config replacement, folder device membership logic. Risks include config restore failure, performance regressions with large device lists, and random ID collision being theoretically possible. Test signal is sync completion and directory equality.
