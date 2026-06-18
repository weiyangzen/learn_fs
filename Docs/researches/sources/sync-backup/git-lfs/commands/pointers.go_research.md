<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pointers.go -->
# sources/sync-backup/git-lfs/commands/pointers.go

Purpose: small helper to collect all wrapped pointers from an asynchronous LFS pointer channel and return the channel's terminal error.

Important APIs/types/functions: `collectPointers` and `lfs.PointerChannelWrapper`.

Control flow: ranges over `pointerCh.Results`, appends every pointer to a slice, then returns the collected slice and `pointerCh.Wait()` error.

State and persistence behavior: in-memory slice only; no persistence.

Dependencies/integration points: helper for scanner/channel APIs elsewhere in commands or adjacent files, preserving channel completion error semantics.

Risks and test signals: risks include unbounded memory use for large pointer sets and blocking forever if producer never closes. Test signals include normal pointer collection, empty channel, and propagation of wait errors after result drain.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pointers.go -->
