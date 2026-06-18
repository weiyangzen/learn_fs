<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-drives-spinner.go -->
# sources/object-store/minio-mc/cmd/top-drives-spinner.go

Purpose: provides the Bubble Tea UI model used by `support top drive` to render per-drive IO statistics.

Important APIs/types/functions: `topDriveUI`, `topDriveResult`, `initTopDriveUI`, `Update`, `View`, `driveIOStat`, `generateDriveStat`, `drivesSorter`, `sortDriveIOStat`, and sorter constants.

Control flow: initialization maps disk endpoints to `madmin.Disk` metadata and tracks maximum pool index. Updates handle quit keys, pool navigation, sort-key changes, sort-order toggling, and incoming `topDriveResult` samples. Each sample shifts current stats to previous and stores new stats. `View` filters disks by current pool, computes deltas over a one-second interval, sorts/truncates to requested count, and renders a table with used percent, TPS, read/write/discard MiB/s, await, and utilization.

State and persistence: transient UI state only: previous/current disk stat maps, selected pool, sort mode, and disk metadata.

Dependencies and integration points: consumed by `support-top-drive.go`; depends on Bubble Tea, lipgloss spinner, tablewriter, `madmin.Disk`/`DiskIOStats`, and shared styles/cell constants.

Risks and test signals: rate math assumes 1000 ms intervals and nondecreasing counters; zero total space suppresses metrics and marks endpoints. Tests should cover sorting modes, pool boundaries, healing/scanning markers, zero-space disks, and utilization/await calculations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-drives-spinner.go -->
