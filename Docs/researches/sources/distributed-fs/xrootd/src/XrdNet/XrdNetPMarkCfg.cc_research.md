# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkCfg.cc

## Purpose
`XrdNetPMarkCfg.cc` implements packet-marking configuration, runtime mark selection, and Firefly backend construction. It parses `pmark` directives, optionally loads SciTags JSON definitions, maps paths/VOs/users/roles to experiment and activity IDs, and creates `XrdNetPMarkFF` handles for marked sessions.

## Important APIs, Types, and Functions
The file defines internal `MapInfo`, `ExpInfo`, and `CfgInfo` types plus many static configuration globals under `XrdNetPMarkConfig`. Public entry points are `XrdNetPMarkCfg::Parse()`, `Config()`, and both `Begin()` overloads. Private helpers include `ConfigDefs()`, `ConfigPV2E()`, `ConfigRU2A()`, `FetchFile()`, `LoadFile()`, `LoadJson()`, `Extract()`, `Display()`, and `getCodes()`.

## Control Flow
`Parse()` accumulates directive state: definitions file or fetch command, failure policy, domain filtering, Firefly destination/origin ports, echo interval, path/VO-to-experiment mappings, user/role/default activity mappings, tracing, and enablement flags. `Config()` finalizes that state, validates Firefly configuration, loads definitions when mappings require them, opens `XrdNetMsg` UDP tunnels for collector/origin reporting, determines the local host/domain, and returns a new `XrdNetPMarkCfg` service only when marking remains enabled. `Begin(XrdSecEntity...)` filters by local/remote domain, obtains experiment/activity codes from `scitag.flow` or configured maps, allows a CGI `pmark.appname` override, then delegates to the address-based `Begin()`, which creates and starts an `XrdNetPMarkFF` handle.

## State and Persistence
Most runtime state is process-global and intentionally survives for server lifetime: experiment maps, path/VO maps, UDP message objects, scheduler/trace/error pointers, host/domain strings, and flags. Fetched defs files are temporarily written under `/tmp/XrdPMark-<pid>.json` and unlinked after load. `Cfg` exists only during configuration and is deleted by a local RAII guard in `Config()`.

## Dependencies and Integration Points
The implementation depends on `XrdNetMsg`, `XrdNetPMarkFF`, `XrdNetUtils`, `XrdOucJson`/nlohmann JSON, `XrdOucMapP2X`, `XrdOucProg`, `XrdOucStream`, `XrdSecEntity`, scheduler and tracing utilities. `XrdXrootdConfig` calls `Parse()` and `Config()`, then publishes the resulting `XrdNetPMark*` into environments used by xrootd, HTTP, and HTTP-TPC protocol code.

## Risks and Test Signals
Key risks are global mutable state, incomplete cleanup of `ffDest`/message objects, JSON schema assumptions that can throw, off-by-one ID boundary handling, and map lookup bugs around extracted VO/role tokens versus original strings. Domain filtering depends on reverse names and private-address detection. Tests should cover directive parse variants, missing or malformed defs files under `fail` and `nofail`, local/remote/any domains, CGI scitag precedence, default experiment/activity fallback, role/user mappings, fetched defs cleanup, Firefly collector/origin failure modes, and emitted diagnostics.
