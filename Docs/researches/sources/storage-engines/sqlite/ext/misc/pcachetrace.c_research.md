# sources/storage-engines/sqlite/ext/misc/pcachetrace.c

Purpose: installs a tracing shim for SQLite's process-global page-cache method table, used by the shell `--pcachetrace` option.

Important APIs/types/functions: `pcacheBase` saves `sqlite3_pcache_methods2`; `pcachetraceOut` stores the log stream. Wrappers trace `xInit`, `xShutdown`, `xCreate`, `xCachesize`, `xPagecount`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`. Public calls are `sqlite3PcacheTraceActivate()` and `sqlite3PcacheTraceDeactivate()`.

Control flow: activation fetches current methods with `SQLITE_CONFIG_GETPCACHE2`, installs `ersaztPcacheMethods`, then wrappers log before and sometimes after delegating. Deactivation restores the original table.

State and persistence: global process state and diagnostic output only.

Dependencies/integration: SQLite global config APIs; should be installed before SQLite initialization.

Risks/test signals: activation timing, repeated activation/deactivation, multithreaded global output, and preserving original methods. Test traces during normal page fetch/unpin/rekey/truncate paths, null output, restore behavior, and lifecycle calls.
