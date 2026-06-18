# sources/storage-engines/wiredtiger/src/session/session_compact.c

## Purpose
Implements `WT_SESSION::compact`, including foreground compaction, background compaction control, per-handle compaction setup, timeout/interruption checks, checkpoint scheduling, and cleanup. The long file header documents WiredTiger's cooperative compaction model between btree and block manager.

## Important APIs, Types, and Functions
- `__wti_session_compact` is the public compact method implementation bound in `session_api.c`.
- `__compact_handle_append` gathers file handles through `__wt_schema_worker`, starts block-manager compaction on each, and stores handles in `session->op_handle`.
- `__compact_worker` runs the checkpoint/compact/checkpoint/checkpoint loop over gathered handles.
- `__wt_session_compact_check_interrupted` handles foreground event-handler interruption, background compact disable, and timeout.
- `__wt_compact_check_eligibility` rejects `.wtobj` tiered objects.
- `__wti_session_compact_readonly` provides the read-only vtable failure path.

## Control Flow
The public method first rejects disaggregated storage, handles `background` configuration as a signal to the background compaction server, validates foreground URI requirements, rejects in-memory and transactional contexts, validates object names, and dispatches extension data-source compaction if the URI is not a core btree/table object. For core objects, it initializes `WT_COMPACT_STATE`, reads `free_space_target`, `timeout`, and `dryrun`, uses schema traversal under schema/table locks to gather file handles, and runs the worker if files were found.

The worker optionally performs an initial checkpoint for foreground compact, then up to 100 passes. Each pass runs `__wt_compact` with each handle, tracks whether another pass is worthwhile, treats `EBUSY` as cache-pressure failure, ignores internal `ECANCELED`, and after progress performs two checkpoints with tree dirty marking between them.

## State and Persistence Behavior
Compaction persists through checkpoints. It rewrites selected pages, then checkpoints twice so blocks freed by old checkpoints become truly available and file truncation can happen safely. The file sets `session->compact`, `session->compact_state`, `session->op_handle`, per-handle `compact_skip`, stats such as running/fail/success/pass counters, and block-manager compact start/end state. Cleanup always ends compaction on gathered handles and releases dhandles.

## Dependencies and Integration Points
Depends on block-manager `compact_start`/`compact_end`, btree `__wt_compact`, checkpoint DB code, schema traversal, session dhandle reference management, background compaction server state, event handlers, configuration parsing, verbose/stat infrastructure, transaction context checks, and object-name validation.

## Risks
Compaction is sensitive to checkpoint ordering and handle lifecycle. Missing `compact_end` or dhandle release can leave handles pinned. Incorrect interruption mapping can expose expected background shutdown as warnings or hide foreground cancellation. Adding new storage backends requires rechecking assumptions about block address opacity, checkpoints, and file truncation. Background compact configuration validation must reject incompatible options when disabling the server.

## Test Signals
Coverage should include foreground compact success, timeout, application interruption, background enable/disable/run-once/exclude/free-space configs, in-memory/disaggregated rejection, tiered `.wtobj` rejection, extension data-source compact hooks, cache-pressure `EBUSY`, dry-run mode, checkpoint count/stat behavior, and leak checks for dhandle release after errors.
