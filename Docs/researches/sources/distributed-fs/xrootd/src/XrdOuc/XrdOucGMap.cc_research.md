# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.cc

## Purpose
Implements grid-mapfile loading and distinguished-name to local-user mapping for GSI/HTTP security contexts.

## Important APIs, Types, And Functions
The plugin factory `XrdOucgetGMap` returns a valid `XrdOucGMap` instance or null. The constructor parses parameters `debug`/`dbg` and `to=<seconds>`, selects a map path from argument, `GRIDMAP`, or `/etc/grid-security/grid-mapfile`, checks readability, and loads mappings. `load` parses full, begins-with (`^`), ends-with (`$`), and contains (`+`) entries into an `XrdOucHash<XrdSecGMapEntry_t>`. `dn2user` performs exact lookup first, then scans pattern entries with `FindMatchingCondition`.

## Control Flow
Loading holds an exclusive `XrdSysXSLock`, skips reload when mtime has not advanced unless forced, purges mappings before reading, parses quoted or space-delimited DNs followed by usernames, records mtime, and returns negative errno on I/O errors. Mapping optionally reloads after timeout expiry, then holds a shared lock while looking up or scanning.

## State And Persistence
State is in-memory: validity flag, mapping hash, map filename, last mtime, timeout/notafter, logger/tracer, debug flag, and shared/exclusive lock. Persistent input is the external grid-mapfile; no output is persisted.

## Dependencies And Integration Points
Depends on `XrdOucEnv`, `XrdOucGMap.hh`, `XrdOucTrace`, `XrdOucStream`, `XrdSysE2T`, POSIX `open/stat/access`, and environment variables. It integrates as a shared-library plugin through `extern "C" XrdOucgetGMap`.

## Risks And Test Signals
Risks include parser overrun on malformed lines missing a closing delimiter, username buffer overflow because `dn2user` copies `mc->user.length()` without bounding to `ulen-1`, leaked `tracer` because the destructor is empty, and `load` ignoring its `mf` parameter. Test signals include exact/prefix/suffix/contains matching, timeout reload after mtime changes, deleted map purge, malformed line handling, too-small username buffers, and plugin factory failure on unreadable maps.
