# sources/sync-backup/kopia/internal/mount/mount.go

Purpose: defines the platform-neutral mount control contract and user-facing mount options.

Important APIs/types/functions: `Controller` exposes `Unmount`, `MountPath`, and `Done`; `Options` carries `FuseAllowOther`, `FuseAllowNonEmptyMount`, and `PreferWebDAV`; package `log` is the mount logger.

Control flow: no runtime logic here; build-tagged platform files implement `Directory` and return concrete controllers that satisfy this interface.

State and persistence behavior: no state is held directly. Concrete controllers own mount lifecycle state and temporary mount cleanup.

Dependencies and integration points: consumed by server mount APIs and command code that need an abstract controller independent of FUSE, WebDAV, or Windows `net use`.

Risks and test signals: interface stability matters because server-side mount bookkeeping stores `mount.Controller` values. Tests should use fake controllers and platform-specific integration tests for unmount/done semantics.
