# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_capacity_unix.go

Purpose: Unix-specific capacity reporting for filesystem storage on non-OpenBSD Unix platforms.

Important APIs/types/functions: `(*fsStorage).GetCapacity`, using `syscall.Statfs` style filesystem statistics.

Control flow: the method stats the filesystem containing the storage root and computes total/free bytes from block counts and block size.

State and persistence behavior: read-only inspection of filesystem capacity; no blob state changes.

Dependencies/integration points: used by Kopia capacity reporting and selected via platform build tags. Risks include differences between available/free block fields, filesystem reporting quirks, and integer conversion assumptions. Coverage is mostly indirect through platform-specific builds and shared storage tests that may call capacity.
