<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/repository.go -->
# sources/sync-backup/restic/internal/restic/repository.go

## Purpose
Defines the central repository interfaces, file type aliases, writable file type constraints, blob loading/saving contracts, warmup contracts, and capability bundles used across restic internals.

## Important APIs and Control Flow
`Repository` is the high-level interface for backend access, config, blob operations, index lookup, warmup, and feature versioning. The file also aliases backend file-type constants, declares `WriteableFileType`, `FileTypes`, `LoaderUnpacked`, `SaverUnpacked`, `RemoverUnpacked`, `Lister`, `BlobLoader`, `BlobSaver`, `BlobSaverAsync`, `WarmupJob`, and set/query interfaces. There is little executable flow beyond `WriteableFileType.ToFileType`; the file is a compile-time contract hub used by repository, restorer, UI, check, prune, and self-test code.

## State, Persistence, Dependencies, and Integration
No runtime state is stored here. Dependencies are `context`, `io`, and internal `backend`, `crypto`, and `errors`; persistence behavior is delegated to implementations that satisfy these interfaces.

## Risks and Test Signals
Risks are broad blast radius from interface changes and generic type-set mistakes. Test signal comes indirectly from all packages that compile against these contracts plus targeted tests for helpers such as parallel removal, listers, config, and blob operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/repository.go -->
