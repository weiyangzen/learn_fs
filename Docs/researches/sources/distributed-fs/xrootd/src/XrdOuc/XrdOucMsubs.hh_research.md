<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh

Purpose: Declares the substitution engine and the per-operation data carrier used to expand `$` variables in command/message templates.

APIs and control flow: `XrdOucMsubsInfo` gathers transaction ids, environment, optional name mapper, logical and physical names, mode, flags, misc options, and buffers for lazily generated names. `XrdOucMsubs::Parse()` compiles a template and `Subs()` materializes it as arrays of data pointers and lengths.

State and persistence: `XrdOucMsubsInfo` owns only the generated `pfnbuff`, `rfnbuff`, `pfn2buff`, and `rfn2buff` allocations. `XrdOucMsubs` owns the parsed template and any duplicated unknown variable names.

Dependencies and integration: Exposes predefined environment key constants for CMS, security identity, and instance variables. Integrates with `XrdSysError`, `XrdOucEnv`, and `XrdOucName2Name`.

Risks and test signals: `maxElem` bounds template complexity and callers must size output arrays accordingly. Tests should validate destructor cleanup, mapping of each predefined variable, and behavior when `Env` or `N2N` lacks requested data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMsubs.hh -->
