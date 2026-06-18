<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc

Purpose: implements `xrdmapc`, a diagnostic utility that starts at an XRootD manager node, maps manager/server topology through locate requests, optionally locates/verifies a path, and prints text or JSON output.

Important APIs/types/functions: `clMap` represents managers/servers and links manager, server, and recursive levels; global flags control manager/server listing, verification, quiet mode, JSON, path, and timeout; `MakeURL()` builds `xroot://host//`; `MapCode()` translates XrdCl/XRootD errors into display state and file verification markers; `MapCluster()` recursively locates subscribers; `MapPath()` marks nodes that locate a target path; `PathChk()` stats the path on a server; `PrintMap()` and `PrintJson()` render output; `SetEnv()` tunes XrdCl connection settings; `main()` parses options and orchestrates mapping.

Control flow: after validating the initial `<host>:<port>` with `XrdNetAddr`, the program creates a base node, applies XrdCl environment defaults, and calls `MapCluster()`. Cluster mapping issues `Locate("*")`, splits returned locations into servers and managers, hashes them by address, and recurses into managers. If a path is supplied, `MapPath()` locates it from the base and recursively through managers; `--verify` additionally stats each listed server during text printing. Finally text or JSON is emitted, with warnings for located path nodes not connected to the discovered topology.

State/persistence: all topology data is heap-allocated in linked `clMap` objects and an `XrdOucHash`. The tool writes only stdout/stderr diagnostics.

Dependencies/integration: integrates with `XrdCl::FileSystem::Locate/Stat`, `LocationInfo`, `XrdNetAddr`, `XrdOucHash`, XRootD protocol error codes, and XrdCl default environment settings (`ConnectionWindow`, `ConnectionRetry`, `TimeoutResolution`).

Risks/test signals: recursive topology discovery has no explicit cycle guard beyond hash storage not being consulted before recursing, so cyclic manager graphs can duplicate work or recurse deeply. Some `state` strings are heap-allocated with `strdup()` and never freed, acceptable for a short-lived tool but visible in leak tests. JSON output is hand-built without escaping host/state strings. Tests should cover option parsing, invalid initial nodes, locate errors, no-subscriber handling, manager-only/server-only listings, JSON suppression of stderr, path locate and refresh, verification states, phantom nodes, and cyclic/duplicate manager responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdMapCluster.cc -->
