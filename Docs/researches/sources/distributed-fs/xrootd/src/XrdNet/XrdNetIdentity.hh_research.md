## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.hh

Purpose: Declares static access to the local network identity.

Important APIs and types: `Domain`, `FQN`, and `SetFQN` expose the domain suffix, fully qualified name, and override hook. Constructor/destructor are trivial.

Control flow: No logic in the header; implementation computes values at static initialization and returns stable pointers.

State and persistence: State is entirely static in the implementation. `SetFQN` changes process-local identity only.

Dependencies and integration points: Used by address and interface code to derive local defaults and domain membership.

Risks: Returned pointers refer to static mutable storage and can change after `SetFQN`. Callers must not free or modify them.

Test signals: Compile and call from early initialization paths; verify users tolerate empty domain string and diagnostic `eText`.
