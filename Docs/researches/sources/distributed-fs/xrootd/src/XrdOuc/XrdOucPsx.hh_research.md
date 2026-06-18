<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh

Purpose: Declares the proxy/client configuration state object used to parse and apply XRootD client-side settings.

APIs and control flow: Public methods parse individual directives, perform full client config, configure loaded objects, expose cache context-manager info, and set name-translation roots. Public fields expose materialized cache, mapper, logger, environment, option list, trace/debug, retry, and name-mapping flags to integrating code.

State and persistence: Owns many heap strings for config path, roots, plugin paths, plugin params, and cache params. Holds pointers to externally integrated cache and mapper objects and a list of client option overrides.

Dependencies and integration: Includes cache context-manager declarations and forward-declares core XrdOuc/XrdSys types. It is a central handoff object between config parsing and client/proxy runtime setup.

Risks and test signals: Many fields are public for integration, so ABI and initialization defaults matter. Tests should validate constructor defaults, destructor cleanup, parse method idempotence, root-setting behavior, and consumers of `xPfn2Lfn`/`xLfn2Pfn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPsx.hh -->
