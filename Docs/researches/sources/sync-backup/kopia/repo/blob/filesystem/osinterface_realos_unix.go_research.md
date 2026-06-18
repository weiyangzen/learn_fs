# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_unix.go

Purpose: Unix implementation of stale file handle detection.

Important APIs/types/functions: `realOS.IsStale`, checking Unix `ESTALE` through error unwrapping/classification.

Control flow: the method detects stale filesystem handle errors so `fsImpl.isRetriable` can avoid retrying them indefinitely.

State and persistence behavior: no mutation; it only classifies OS errors that arise from filesystem state changes.

Dependencies/integration points: selected on Unix builds and validated by Unix filesystem tests. Risks include errno wrapping differences and NFS/filesystem-specific stale behavior. Correct classification matters because stale handles usually indicate an invalid descriptor/resource rather than a transient path operation.
