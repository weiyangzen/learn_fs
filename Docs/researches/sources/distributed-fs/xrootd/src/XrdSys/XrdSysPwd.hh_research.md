# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPwd.hh

Purpose: wraps thread-safe passwd database lookups in a small object with reusable storage.

Important APIs/types/functions: `XrdSysPwd::Get(const char *)`, `Get(uid_t)`, constructors that immediately call `getpwnam_r()` or `getpwuid_r()`, public `rc`, and private `passwd`/buffer storage.

Control flow: callers either construct and call `Get()` repeatedly or construct with a user/UID and receive a `passwd **`. Each lookup writes into `pwStruct` backed by `pwBuff` and stores the returned pointer in `Ppw` or caller-provided pointer.

State and persistence: returned `passwd *` points into the `XrdSysPwd` instance; it is invalid after the object is destroyed or another lookup overwrites the buffer. No global state is changed.

Dependencies and integration: uses POSIX `<pwd.h>` reentrant functions and is consumed by privilege handling to resolve usernames before temporary credential switches.

Risks: fixed 4096-byte buffer may be too small for unusual passwd entries, yielding an error in `rc`. `Ppw` is not initialized by the default constructor until `Get()` is called. Consumers must not store returned pointers beyond object lifetime.

Test signals: lookup known user, lookup invalid user, lookup by current UID, and simulate/verify `ERANGE` handling on systems with large passwd records.
