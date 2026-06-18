# sources/user-network-fs/blobfuse2/component/azstorage/azstorage.go

Purpose: implements the `azstorage` BlobFuse pipeline component. It adapts the component interface to an `AzConnection` backend, manages config validation, startup/shutdown, list blocking on mount, handle creation, stats collection, and filesystem operation forwarding.

Important APIs/types/functions: `AzStorage` embeds `internal.BaseComponent` and holds `storage AzConnection`, `stConfig AzStorageConfig`, `startTime`, and `listBlocked`. Core methods include `Configure`, `OnConfigChange`, `configureAndTest`, `Start`, `Stop`, directory methods (`CreateDir`, `DeleteDir`, `IsDirEmpty`, `ReadDir`, `StreamDir`, `RenameDir`), file methods (`CreateFile`, `OpenFile`, `ReleaseFile`, `DeleteFile`, `RenameFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `GetFileBlockOffsets`, `TruncateFile`, `CopyToFile`, `CopyFromFile`), symlink/attribute methods, and block staging/commit methods.

Control flow: configuration unmarshals azstorage options, parses/validates them, creates an `AzConnection`, sets up and tests the pipeline in parent mode, and auto-reconfigures from flat blob to ADLS when account detection says HNS and account type was not explicit. `Start` initializes list-block timing and stats. `ReadDir` and `StreamDir` optionally return empty results until `cancelListForSeconds` has elapsed. Listing uses continuation markers; `StreamDir` recursively retries when Azure returns an empty page with a non-empty marker. File operations mostly forward to `storage`, adding handle bookkeeping and stats events.

State and persistence behavior: state is runtime-only: storage client, parsed config, list-block timer, and global `azStatsCollector`. The component does not persist data itself; persistence happens through the storage backend. Dynamic config updates mutate the existing storage config and SDK log listener.

Dependencies/integration: depends on config/log/common packages, `internal.Component`, `handlemap`, `stats_manager`, Cobra flag registration, and the `AzConnection` implementations such as `BlockBlob`. It registers itself as component `azstorage` and binds many hidden and visible CLI flags.

Risks: `Stop` assumes `azStatsCollector` is non-nil after `Start`; unusual lifecycle calls could panic. `ReadLink` appears to push stats only when `err != nil`, which likely counts failed reads instead of successful reads. `ReadInBuffer` uses handle size or provided size to clamp reads and returns `ERANGE` when offset is beyond size; stale handle size could hide valid appended data until refreshed. `Configure` uses a `goto` reconfiguration path, so config parsing must remain idempotent.

Test signals: `azauth_test.go` exercises setup/test pipeline behavior for auth configurations. Operation-level behavior is likely covered by separate azstorage tests outside this subset.
