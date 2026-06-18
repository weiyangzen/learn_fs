## sources/sync-backup/syncthing/lib/model/sentdownloadstate.go

Purpose: tracks which partial download blocks have already been advertised to a remote device so download-progress messages can be sent as append/forget deltas instead of full state snapshots.

Important types and functions: `sentFolderFileDownloadState` stores block indexes, version, creation time, update time, and block size for one file. `sentFolderDownloadState.update` compares active `sharedPullerState` instances to previously sent state and emits `protocol.FileDownloadProgressUpdate` values. `destroy` emits forget updates for all tracked files. `sentDownloadState` groups folder states and exposes `update`, `folders`, and `cleanup`.

Control flow and state: each update pass builds a `seen` set from active pullers. New files are announced only when they have at least one available block. Existing files are ignored when available-block timestamp and version match. Version or puller recreation changes trigger a forget for the old version followed by append for the new state. Otherwise the code assumes `sharedPullerState.Available()` is append-only and slices new block indexes from the previous length. Pullers missing from the pass are treated as completed or failed and generate forget updates.

Dependencies and integration points: reads `sharedPullerState.file`, `Available`, `AvailableUpdated`, and `created`, and emits protocol download progress updates consumed by BEP connections. It is used from a single progress emitter routine, so it deliberately has no locking.

Risks: correctness depends on append-only ordering and stable timestamps from `sharedPullerState`; if the available slice is reordered or truncated, slicing by previous length can panic or send wrong deltas. Map iteration makes forget ordering nondeterministic. Lack of internal synchronization is acceptable only while the single-routine invariant holds.

Test signals: no direct test in this subset. Indirect coverage appears in request/progress tests such as `TestRequestLastFileProgress` and protocol download progress serialization.
