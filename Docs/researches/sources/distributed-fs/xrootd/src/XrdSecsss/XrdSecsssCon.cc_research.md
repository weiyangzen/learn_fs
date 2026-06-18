# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.cc

Purpose: implementation of contact tracking for mapped SSS identities. It records outbound contacts against a registered login ID so they can be cleaned up when the identity is unregistered.

Important API: `XrdSecsssCon::Contact(const std::string &lgnid, const std::string &hostID)` is the only function. It is paired with the abstract `Cleanup()` declared in the header.

Control flow: the method first verifies this object is the process-global tracker. It extracts the login portion before `@`, strips an optional password after `:`, validates size and shape, locks the global SSS registry, looks up the login ID, and calls `XrdSecsssEnt::AddContact()` on the mapped entity.

State and persistence: no persistence. Runtime state is global `conTrack`, global `Registry`, and each entity's in-memory `Contacts` set.

Dependencies and integration: uses `XrdSecsssMap` globals shared with `XrdSecsssID`, and `XrdSecsssEnt` to store contacts. Cleanup is invoked from entity deletion.

Risks: the `lgnid` parameter is unused; the login is derived from `hostID`. Invalid host strings are silently rejected. Global locking protects map access, but cleanup behavior depends on external subclass correctness.

Test signals: register mapped identities, add duplicate and distinct contacts, verify password stripping, reject malformed host IDs, unregister and assert subclass `Cleanup()` receives the expected set and entity.
