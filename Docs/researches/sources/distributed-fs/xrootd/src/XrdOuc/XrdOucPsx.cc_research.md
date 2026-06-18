<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc

Purpose: Implements parsing and materialization of proxy/client-side XRootD configuration for caching, name translation, network mode, trace/debug, and client options.

APIs and control flow: `ClientConfig()` opens the config file, reads directives matching a prefix, dispatches to `Parse()`, captures diagnostics when `hush` is enabled, and then calls `ConfigSetup()`. `ConfigSetup()` loads cache libraries, cache context manager plugins, and name translation. `ParseCache()` builds cache parameter strings including size, pages, preread, stats, and write options. `ParseCLib()`, `ParseMLib()`, `ParseNLib()`, `ParseCio()`, `ParseINet()`, `ParseSet()`, and `ParseTrace()` validate and store directive state. `ConfigCache()`, `LoadCCM()`, and `ConfigN2N()` instantiate configured plugins through `XrdOucPinLoader` and `XrdOucN2NLoader`.

State and persistence: The object owns config strings, plugin paths/params, set-option lists, cache and name-mapper pointers, trace/debug levels, inet mode, and cache behavior flags. Environment exports and loaded plugins affect process state.

Dependencies and integration: Ties together `XrdOuca2x`, `XrdOucCache`, `XrdOucN2NLoader`, `XrdOucPinLoader`, `XrdOucStream`, `XrdOucTList`, and `XrdSysLogger`.

Risks and test signals: `SetRoot()` appears to call `strdup(lroot)` even after `lroot` is null because the assignment block is unconditional. Parser tests should cover every directive, hush diagnostics, default cachelib translation, unsupported setopts, namelib/cache interactions, plugin failures, and null-root handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.cc -->
