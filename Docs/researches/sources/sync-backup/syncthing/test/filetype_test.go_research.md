# Research: sources/sync-backup/syncthing/test/filetype_test.go

## sources/sync-backup/syncthing/test/filetype_test.go

Purpose: verifies synchronization when filesystem object types change between file and directory under different receiver versioning modes.

Important APIs/functions: `TestFileTypeChange`, `TestFileTypeChangeSimpleVersioning`, `TestFileTypeChangeStaggeredVersioning`, and shared `testFileTypeChange`.

Control flow: each wrapper edits `h2/config.xml` to set no/simple/staggered versioning, preserving the original config. The shared test creates files and directories that are later replaced by the opposite type, syncs initial state, delays sender scans, performs replacements, rescans, awaits sync, and compares `s1`/`s2`.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, and temporarily rewrites h2 config.

Dependencies and integration: `lib/config`, `events`, `protocol`, `rc`, and versioner implementations. Risks include platform filesystem semantics, versioner interaction with replaced directories, and config restore failures. Test signal is exact directory equality after type changes.
