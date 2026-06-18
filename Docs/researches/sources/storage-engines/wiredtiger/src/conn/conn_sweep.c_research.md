# sources/storage-engines/wiredtiger/src/conn/conn_sweep.c

## Purpose
This file implements the handle sweep server. It marks idle data handles with a time of death, closes clean open handles, discards dead btrees, removes unreferenced handles from the connection list, and emits diagnostics for sessions that have not swept cursor/dhandle references.

## Important APIs, Types, and Functions
Public functions are `__wti_sweep_config`, `__wti_sweep_create`, and `__wti_sweep_destroy`. Core helpers include `__sweep_mark`, `__sweep_expire`, `__sweep_discard_trees`, `__sweep_remove_handles`, `__sweep_remove_one`, `__sweep_expire_one`, `__sweep_close_dhandle_locked`, `__sweep_file_dhandle_check_and_reset_tod`, `__sweep_check_session_sweep`, and the server thread `__sweep_server`. Important macros/state include `WT_DHANDLE_CAN_DISCARD`, `WT_DISAGG_OUTDATED_GRACE_SECS`, dhandle flags, `conn->sweep`, and `conn->dhqh`.

## Control Flow and Behavior
Configuration sets idle time to zero for in-memory mode, otherwise reads file-manager close idle time, scan interval, and minimum handle count. Create sets `WT_CONN_SERVER_SWEEP`, opens an internal session with wait and ignore-cache-size flags, allocates a condition, and starts the server.

The server waits for interval or signal, skips full sweeps during checkpoint handle gathering, marks idle non-metadata handles, expires handles when above the minimum or in disaggregated mode, discards pages from dead open handles, removes closed unreferenced handles, checks stale session sweep activity, and in disaggregated leader mode marks the shared disk cache dead after the readonly grace window. Table handles get extra checks so simple table handles stay alive while their file dhandle exists. Layered and history-store handles are not marked for normal idle sweep.

## State and Persistence
Sweep state is in memory: dhandle `timeofdeath`, flags, reference counts, open counts, server session/thread/condition, sweep config, and session warning booleans. It changes persistent effects indirectly by closing/discarding handles and removing local dhandle structures, not by writing metadata.

## Dependencies and Integration Points
The file depends on handle-list locks, table locks, dhandle write locks, checkpoint state, btree modified state, connection dhandle close/discard functions, session array walks, disaggregated shared disk cache state, and statistics. It integrates with connection close and reconfigure through create/destroy/config calls.

## Risks
Risks include closing a handle still needed by active sessions, table/file handle ordering races, interference with checkpoint handle gathering, deadlocks from lock order, retaining too many handles when session references are not swept, and disaggregated outdated checkpoint handles being closed before the shared disk cache reuse window expires.

## Test Signals
Signals include sweep statistics for time-of-death, expired close, dead close, remove, ref skips, checkpoint skips, and no-session-sweep warnings. Behavioral tests should cover table/file dhandle retention, history-store/layered exclusions, disaggregated outdated checkpoint cleanup, and clean shutdown of the sweep server.
