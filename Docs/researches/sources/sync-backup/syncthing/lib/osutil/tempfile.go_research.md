## sources/sync-backup/syncthing/lib/osutil/tempfile.go

Purpose: filesystem-abstracted temporary file creation adapted from Go's temp-file approach.

Important APIs: internal `reseed` and `nextSuffix`, and exported `TempFile(filesystem, dir, prefix)`.

Control flow and state: a package atomic counter is seeded from random data and incremented for suffixes. `TempFile` defaults empty dir to `.`, tries up to 10,000 generated names, creates files with `OptReadWrite|OptCreate|OptExclusive` and mode `0600`, and handles existing-file collisions by retrying. If a name-generation collision pattern persists it reseeds.

Dependencies and integration points: used by `AtomicWriter` and other fs-abstracted temp-file code. Depends on Syncthing `fs.Filesystem` and crypto-random package `rand`.

Risks: failure to create after many attempts returns the last error or a too-many-attempts error. Security depends on exclusive create and mode `0600` support by filesystem implementation.

Test signals: `atomic_unix_test.go` indirectly validates temp permissions.
