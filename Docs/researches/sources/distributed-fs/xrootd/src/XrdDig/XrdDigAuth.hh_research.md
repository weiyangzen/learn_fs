## sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.hh

### Purpose
This header declares the digFS authorization record and authorization manager.

### Important APIs, Types, and Functions
- `XrdDigAuthEnt` is one ACL record. It stores `next`, a packed `rec` allocation, `prot`, entity-check pointers, and per-resource `accOK` flags.
- `XrdDigAuthEnt::eType` indexes entity selectors: name, host, virtual organization, role, and group.
- `XrdDigAuthEnt::aType` indexes protected dig resources: `conf`, `core`, `logs`, and `proc`; `aNum` is also used as a sentinel for vector queries.
- `XrdDigAuth` exposes `Configure` and `Authorize` and keeps refresh/parsing helpers private.

### Control Flow
The public contract is intentionally small: initialize with an auth-file path, then authorize clients against a requested resource. Private helpers parse and refresh the list on demand.

### State and Persistence
`XrdDigAuth` owns a mutex, the auth-file path, mtime and next-check timestamps, a linked list of ACL records, and a summary access mask. Individual entries own one packed record buffer released in the destructor.

### Dependencies and Integration Points
The header includes `XrdSecEntity.hh` and `XrdSysPthread.hh`, making the authorization manager directly tied to XRootD security identity and mutex primitives. It is consumed by `XrdDigAuth.cc` and `XrdDigConfig.cc`.

### Risks and Edge Cases
The `XrdDigAuth` destructor does not free `authFN` or the linked `authList`; process lifetime likely owns these globals, but repeated construction in tests would leak. `memset` initialization assumes plain pointer/bool layout. The packed-buffer model requires pointer relocation to be correct after parse.

### Test Signals
Header-level tests are compile/interface tests: enum order must match token arrays in `XrdDigAuth.cc` and `XrdDigConfig.cc`, `aNum` must size all access vectors, and `XrdSecPROTOIDSIZE` must bound protocol strings.
