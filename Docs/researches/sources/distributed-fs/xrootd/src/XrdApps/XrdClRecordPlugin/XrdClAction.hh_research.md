<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh

Purpose: defines the serializable action model used by the XrdCl recorder plugin. Each operation type captures its request arguments, timing, status, and optional response summary for later replay.

Important APIs/types/functions: base `Action` stores file id, timeout, start/stop times, `XRootDStatus`, and serialized response; `RecordResult()` records completion state; `time()` and `timeNow()` produce Unix seconds with nanosecond precision; `ToString()` emits a quoted CSV row. Derived actions include `OpenAction`, `CloseAction`, `StatAction`, `ReadAction`, `PgReadAction`, `WriteAction`, `PgWriteAction`, `SyncAction`, `TruncateAction`, `VectorReadAction`, `VectorWriteAction`, and `FcntlAction`.

Control flow: the recorder creates a specific action before submitting an async operation. On callback, `RecordResult()` captures the status/response and `ToString()` serializes the row as `id,name,start,args+timeout,stop,status,response`.

State/persistence: action instances are transient, but their `ToString()` output is persisted by `Recorder::Output`. The file id is the recording plugin object's pointer cast to `uint64_t`, making it a per-process correlation key rather than a stable identity.

Dependencies/integration: depends on `XrdClXRootDResponses` response types such as `StatInfo`, `ChunkInfo`, `PageInfo`, and `VectorReadInfo`, plus XrdCl flag/mode/chunk types used by replay parsing.

Risks/test signals: CSV escaping is minimal and assumes arguments/status/response do not contain embedded quotes that need escaping. `ToString()` trims trailing spaces from `status.ToString()` by calling `ststr.back()`, which assumes a non-empty status string. `TruncateAction` stores a `uint64_t` argument into a `uint32_t size` member. Tests should verify every action's argument format round-trips through `XrdClReplay`, response serialization for null responses, large truncate sizes, vector chunk ordering, and status string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClAction.hh -->
