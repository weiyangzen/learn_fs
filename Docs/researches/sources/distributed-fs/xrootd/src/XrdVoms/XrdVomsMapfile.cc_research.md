# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.cc

Purpose: Implements optional VOMS FQAN-to-local-username mapping from a mapfile with live reload.

Important APIs/types/functions: Static singleton mapper and tried_configure gate global configuration. Constructor stats/parses the mapfile and starts MaintenanceThread(). ParseMapfile(), ParseLine(), Map(), Compare(), MakePath(), Apply(), Get(), Configure(), and MaintenanceThread() form the implementation.

Control flow: Configure() imports XRDCONFIGFN, reads XRootD config through XrdOucStream, handles voms.mapfile and voms.trace directives, creates the singleton, and returns null, VOMS_MAP_FAILED, or a mapper. ParseLine() accepts quoted FQAN-like paths and printable targets with escapes. Apply() respects successful gridmap.name mappings first, tokenizes entity.vorg/role/grps in parallel, enforces that the FQAN root equals the VO, appends Role=... and Capability=NULL, maps the first matching entry, and replaces entity.name. MaintenanceThread() sleeps 30 seconds, stats ctime, and reparses on change.

State/persistence: Runtime singleton stores mapfile path, last ctime, atomic-ish shared_ptr entries snapshot, error stream, and validity flag. Persistent input is the configured mapfile.

Dependencies/integration: Uses XrdOucEnv, XrdOucStream, XrdOucString wildcard matches, XrdSecEntity extended attributes, XrdSysError, XrdSysThread, and POSIX stat/open.

Risks: Maintenance thread runs forever with no shutdown path. m_is_valid is read/written across threads without atomic protection. ParseLine grammar is strict and may silently skip malformed lines. Configure caches failure and will not retry a later fixed config in the same process.

Test signals: Test mapfile parsing with escapes/comments/invalid lines, wildcard matching, gridmap precedence, VO root enforcement, parallel token lengths, live ctime reload, missing config file, trace mask parsing, and thread-safety under concurrent Apply() while reloading.
