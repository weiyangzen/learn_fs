# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.hh

Purpose: declares the SSS keytab manager and key entry representation.

Important APIs and types: nested `ktEnt` defines maximum key/name/user/group sizes, `ktData`, option bits `allUSR`, `anyUSR`, `anyGRP`, `usrGRP`, and `noIPCK`, plus helpers `NUG()` and `Set()`. `XrdSecsssKT` exposes add/delete/get/list/refresh/rewrite/path APIs, `genFN()`, `genKey()`, and mode enum `isAdmin`, `isClient`, `isServer`.

Control flow: callers construct with an error object, keytab path, mode, and refresh interval. Admin mode mutates and rewrites keytabs; client/server modes use lookup and background refresh.

State and persistence: header declares linked-list key state, keytab path, mtime, mode, refresh interval, mutex, refresh thread ID, and static random fd. Persistence format is implemented in the `.cc`.

Dependencies and integration: includes time, string/memory helpers, and `XrdSysPthread`. Used by protocol, RR header for key-name size, and admin CLI.

Risks: fixed-size char arrays require strict bounds in parser and CLI. `ktEnt::Set()` copies only selected fields, intentionally not name/user/group/options, which is correct for same-NUG replacement but risky if misused elsewhere.

Test signals: compile users against constants, verify option-bit effects in protocol auth, and unit-test `Same()`, `setPath()`, key list ownership, and lifecycle with refresh threads.
