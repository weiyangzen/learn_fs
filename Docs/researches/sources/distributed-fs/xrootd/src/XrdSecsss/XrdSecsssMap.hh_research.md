# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssMap.hh

Purpose: shared internal declarations for the SSS identity registry namespace.

Important APIs and types: declares global `XrdSysMutex sssMutex`, `XrdSecsssID *IDMapper`, `XrdSecsssCon *conTrack`, `typedef std::map<std::string, XrdSecsssEnt*> EntityMap`, and external `Registry`.

Control flow: no executable code. It lets `XrdSecsssID.cc`, `XrdSecsssCon.cc`, and entity code share the same registry and lock.

State and persistence: declares process-global in-memory state only. Definitions live in `XrdSecsssID.cc`.

Dependencies and integration: includes C++ map/string and forward declarations, but relies on `XrdSysMutex` being visible from includers; this works because implementation files include mutex headers before or through other headers.

Risks: global mutable registry creates singleton semantics and can complicate tests. Header does not include the mutex type declaration directly, making include-order assumptions fragile.

Test signals: compile include-order checks, registry operations under concurrency, and teardown behavior when mapped entities are deleted.
