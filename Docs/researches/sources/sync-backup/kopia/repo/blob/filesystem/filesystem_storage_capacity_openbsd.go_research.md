# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_openbsd.go

Purpose: OpenBSD-specific capacity reporting for filesystem storage.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, using platform `statfs` fields appropriate for OpenBSD.

Control flow: the method queries filesystem statistics for the storage root and converts block counts/sizes into total and free byte counts, returning a `blob.Capacity`.

State and persistence behavior: read-only capacity inspection; it does not mutate files.

Dependencies/integration points: selected by Go build constraints for OpenBSD and used by generic repository capacity queries. Risks include platform-specific field semantics and overflow/conversion issues. Test coverage is likely indirect because capacity behavior is platform dependent and normal CI may not run OpenBSD.
