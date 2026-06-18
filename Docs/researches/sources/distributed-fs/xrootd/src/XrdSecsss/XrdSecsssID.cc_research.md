# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.cc

Purpose: implements the optional process-wide login-ID-to-entity registry for SSS clients.

Important APIs and functions: constructor `XrdSecsssID::XrdSecsssID()`, private destructor, `Find()`, static `genID()`, static `getObj()`, and public `Register()`. Namespace `XrdSecsssMap` defines global mutex, mapper pointer, contact tracker, and registry map.

Control flow: only one mapper can be effective. Construction validates auth type, creates a default identity, installs the global mapper, and optionally enables contact tracking for mapped modes. `getObj()` returns current auth mode and default identity, generating one if needed. `Register()` adds, replaces, or removes mappings under lock. `Find()` looks up a login ID and falls back to default identity, returning serialized RR data.

State and persistence: all state is in process memory: global mapper, registry, default identity, and contact tracker. `genID()` derives identity from process uid/gid unless secure mode forces `nobody/nogroup`, and may set endorsements from `XrdSecsssENDORSEMENT`.

Dependencies and integration: used by `XrdSecProtocolsss::Load_Client()` and credential generation. Depends on `XrdSecEntity`, `XrdSecsssEnt`, `XrdSecsssMap`, `XrdOucUtils`, and `XrdSysMutex`.

Risks: singleton behavior means later construction is ineffective. Deferred registration can store pointers to mutable external entities. `Find()` calls `RR_Data()` while holding the global mutex, so serialization cost and callbacks can extend lock hold time.

Test signals: singleton construction, each auth type, default identity generation, register/replace/delete behavior, mapped fallback, environment endorsements, and concurrent register/find access.
