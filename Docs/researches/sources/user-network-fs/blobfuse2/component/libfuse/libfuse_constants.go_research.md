# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_constants.go

Purpose: centralizes string constants used by libfuse stats/event reporting.

Important APIs/types/functions: constants name operations (`CreateDir`, `DeleteDir`, `CreateFile`, `TruncateFile`, `DeleteFile`, `RenameDir`, `RenameFile`, `CreateLink`, `ReadLink`, `SyncFile`, `SyncDir`, `Chmod`), gauge/counter key `OpenFileHandles`, and event metadata keys (`Mode`, `Size`, `Src`, `Dest`, `Target`).

Control flow: no executable control flow. Handler callbacks use these constants when calling `libfuseStatsCollector.PushEvents` and `UpdateStats`.

State and persistence behavior: no mutable state. Constants influence the names under which runtime stats/events are recorded and therefore the external observability schema.

Dependencies/integration points: imported within libfuse package handler files; coupled to `stats_manager.StatsCollector` consumers and any dashboards/log processors expecting these exact names.

Risks: changing strings is a compatibility break for metrics consumers. The file does not include constants for every callback (`OpenFile`, `ReadFile`, `WriteFile`, `FlushFile`, `ReleaseFile`, `Chown`, `Utimens` are absent), reflecting current instrumentation gaps.

Test signals: no direct tests. Indirect coverage occurs when callback tests exercise handlers that push events or update stats, but assertions generally focus on return codes and component options rather than emitted metric names.
