# Research: sources/sync-backup/syncthing/test/symlink_test.go

## sources/sync-backup/syncthing/test/symlink_test.go

Purpose: verifies symlink synchronization and symlink replacement/removal behavior under multiple receiver versioning modes.

Important APIs/functions: `TestSymlinks`, `TestSymlinksSimpleVersioning`, `TestSymlinksStaggeredVersioning`, and shared `testSymlinks`.

Control flow: skips when symlinks are unsupported, temporarily rewrites h2 versioning, creates files, directories, valid symlinks, broken symlinks, and replacement targets, syncs initial state, then removes, retargets, and replaces symlinks with files/directories and vice versa. After rescan and sync, directories are compared.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, symlink entries, and h2 config.

Dependencies and integration: OS symlink support, scanner file type detection, puller replacement logic, versioning behavior. Risks include platform-specific symlink permissions and versioner interaction with link replacement. Test signal is exact directory equality.
