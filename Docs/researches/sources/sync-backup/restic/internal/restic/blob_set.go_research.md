
# sources/sync-backup/restic/internal/restic/blob_set.go

Purpose: implements `BlobSet`, a map-backed set of `BlobHandle` values.

Important APIs include `NewBlobSet`, `Has`, `Insert`, `Delete`, `Len`, `Equals`, `Merge`, `Intersect`, `Sub`, `List`, and `String`. `List` returns sorted blob handles. `String` renders a compact stable representation, truncating after ten entries with a count of remaining entries to keep logs/errors readable.

State is in-memory only but frequently represents used, keep, remove, duplicate, or missing blob sets. Integration points include prune planning, repack keep sets, repair tests, checker diagnostics, and user-facing errors about missing blobs. Risks include map iteration nondeterminism if not sorted before display, large set logging, and set mutation while shared across goroutines; concurrent users add explicit locking elsewhere. `blob_set_test.go` verifies empty, single, and truncated string formats.
