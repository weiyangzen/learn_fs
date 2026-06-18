## sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams.go

### Purpose
`kernelparams.go` manages kernel parameter tuning for GCSFuse mounts. It can write the shared JSON contract for a privileged CSI driver in GKE, or directly mutate host procfs/sysfs values in non-GKE environments.

### Important APIs, Types, And Functions
`KernelParamsManager` embeds `*KernelParamsConfig` and guards it with a mutex. Public methods are `NewKernelParamsManager`, `PathForParam`, `ShouldUpdateMaxPagesLimit`, setter methods for each supported parameter, `ApplyGKE`, and `ApplyNonGKE`. Internal helpers are `readMaxPagesLimitFunc`, `getDeviceMajorMinor`, `atomicFileWrite`, `writeValue`, `applyDirectly`, and `addParam`.

### Control Flow
Setters validate positive/nonempty values and upsert parameters. `ApplyGKE` exits if there are no params, marshals the config, and atomically writes it. `ApplyNonGKE` resolves device major/minor from the mount point, maps each parameter to procfs/sysfs paths, then writes values directly or via non-interactive `sudo tee` on permission errors. `ShouldUpdateMaxPagesLimit` reads the current shared machine limit and only recommends increasing it.

### State, Persistence, And Dependencies
Manager state is in-memory until written. GKE persistence is an atomic JSON file in the caller-provided path. Non-GKE persistence is host kernel state under `/proc/sys/fs/fuse`, `/sys/class/bdi`, `/sys/fs/fuse/connections`, and `/sys/kernel/mm/transparent_hugepage`. Dependencies include `os`, `exec`, `encoding/json`, `syscall.Stat_t`, `x/sys/unix`, and the global logger.

### Integration Points
This package integrates with mount configuration and GKE sidecar/CSI flows. It is Linux-specific for direct application. The direct path depends on FUSE connection minor numbers and BDI major/minor derived from the mount point.

### Risks
Direct kernel writes are privileged and environment-sensitive; sudo fallback only works with passwordless sudo and may be inappropriate in unattended contexts. `writeValue` uses file mode `0644` for direct writes, although existing sysfs/procfs permissions usually dominate. Holding the manager mutex through file writes/sysfs mutations can block concurrent setter/apply calls. Machine-level `max_pages_limit` safety relies on successfully reading the existing value.

### Test Signals
Tests cover atomic writes, Linux major/minor extraction, path mapping, setter upserts, empty/no-op GKE application, direct write success/failure, sudo fallback behavior, and `ShouldUpdateMaxPagesLimit` branches. Real sysfs/FUSE connection mutation is not integration-tested.
