# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.hh

Purpose: declares the SSS entity serialization and contact-tracking object used by the protocol client side and ID mapper.

Important APIs and types: public fields `eData`, `iLen`, and `tLen` expose packed data and lengths. Methods include `AddContact()`, `Delete()`, `RR_Data()`, `Ref()`, `UnRef()`, and static `setHostName()`. Constants `addExtra`, `addCreds`, and `v2Client` control serialized data detail.

Control flow: construction stores an `XrdSecEntity` pointer and serializes immediately unless `defer` is true. Destruction is private; callers use `Delete()` or reference counting.

State and persistence: owns malloc-packed identity data, reference count, optional contacts, credential length, and static hostname buffer. No persistent storage.

Dependencies and integration: uses `XrdSysAtomics`/mutex fallback, C++ sets, and `XrdSecEntity`. It is stored in `XrdSecsssID` registries and consumed by `XrdSecProtocolsss::getCred()`.

Risks: public packed-data members expose mutable internals. Deferred mode depends on external entity lifetime. Manual ref counting can conflict with `Delete()` if ownership rules are mixed.

Test signals: construct immediate/deferred entities, call `RR_Data()` repeatedly, verify reference count deletion, and run under leak/thread sanitizers around contact cleanup.
