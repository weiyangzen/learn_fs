<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh

Purpose: Provides a template orchestrator for post-R5 object-oriented plugin loading, including stacked plugin chains.

APIs and control flow: `Add()` records a base plugin or pushes an additional stacked plugin. `Load(Symbol)` iterates configured pins, creates an `XrdOucPinLoader` for each path, resolves an `XrdOucPinObject<T>` symbol, and calls `getInstance(parms, env, logger, previous)` so each plugin can wrap or extend the previous instance.

State and persistence: `pinVec` stores path, parameters, and loader pointers. `pinInfo` deletes its loader, whose destructor persists successfully loaded plugin images. The returned plugin instance is owned by the caller or plugin contract.

Dependencies and integration: Integrates `XrdOucPinLoader`, `XrdOucPinObject`, `XrdOucEnv`, `XrdSysError`, and caller version metadata.

Risks and test signals: `Add(push=false)` assumes the constructor-created base slot exists. Partial chain failures return null and leave prior instances to plugin-specific ownership rules. Tests should cover base replacement, stacked loading order, missing symbols, bad parameters, and loader persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinKing.hh -->
