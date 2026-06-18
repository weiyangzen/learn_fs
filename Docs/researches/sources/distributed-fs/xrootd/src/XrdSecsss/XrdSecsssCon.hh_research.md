# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.hh

Purpose: abstract interface for tracking and cleaning contacts created by SSS mapped identities.

Important APIs: subclasses implement `Cleanup(const std::set<std::string>&, const XrdSecEntity&)`. Concrete `Contact(const std::string &lgnid, const std::string &hostID)` records a connection in the registered entity if tracking is enabled.

Control flow: lifecycle is external. A tracker is passed to `XrdSecsssID`; when an entity is deleted, `XrdSecsssEnt::Delete()` calls `Cleanup()` with the accumulated contacts and entity, then deletes the entity.

State and persistence: the interface itself owns no state. Contact state lives in `XrdSecsssEnt`.

Dependencies and integration: includes C++ `set` and `string`, forward declares `XrdSecEntity`, and integrates with `XrdSecsssID` construction.

Risks: cleanup is synchronous and subclass-defined, so slow or throwing implementations could affect unregister paths. The comments say contacts use `user[:pswd]@host:port`; password-bearing strings require careful downstream handling.

Test signals: compile a mock subclass, pass it into mapped ID mode, call `Contact()`, unregister identities, and verify cleanup ordering and ownership expectations.
