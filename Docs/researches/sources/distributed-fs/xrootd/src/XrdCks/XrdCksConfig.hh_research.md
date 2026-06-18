# sources/distributed-fs/xrootd/src/XrdCks/XrdCksConfig.hh

Purpose: declares `XrdCksConfig`, the object that parses and materializes checksum manager configuration.

Important APIs: public `Configure()`, `Manager()`, `ParseLib()`, and `ParseOpt()` create or configure checksum managers. `Manager()` also reports whether a custom manager path is set. Private helpers are `addCks()` and `getCks()`.

State and persistence: stores the config filename, manager library path and parameters, linked lists for checksum and stackable libraries, last-list pointers, plugin version info, and option flags. This state is runtime configuration only.

Dependencies and integration: includes `XrdOucTList.hh` and forward-declares `XrdCks`, `XrdOss`, `XrdOucEnv`, `XrdOucStream`, `XrdSysError`, and `XrdVersionInfo`.

Risks and test signals: API tests should verify constructor version acceptance/rejection, `Manager()` state transitions, and `Configure()` behavior with OSS-backed versus native managers.
