## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixAdmin.hh

Purpose: declares `XrdPosixAdmin`, a small URL-bound administrative facade for XRootD filesystem metadata and query operations.

Important APIs/types: public members `Url`, `Xrd`, and `ecMsg`; methods `isOK()`, `FanOut()`, `Query()` overloads, and `Stat()` overloads. Constructor binds a path string to `XrdCl::URL` and `XrdCl::FileSystem`.

Control flow: callers construct an admin object per path/URL and call an operation. `isOK()` centralizes URL validation, fills `ecMsg`, and sets `errno=EINVAL` on invalid URLs.

State and persistence: owns an `XrdCl::URL` and `XrdCl::FileSystem` by value; references an external `XrdOucECMsg`. It writes no durable state.

Dependencies/integration: includes `XrdClFile`, `XrdClFileSystem`, `XrdClURL`, XRootD response types, and `XrdOucECMsg`. It is used by `XrdPosixDir`, `XrdPosixExtra`, and stat/administrative paths.

Risks: public mutable members allow callers to alter URL/filesystem state directly. `ecMsg` lifetime must exceed the admin object. `isOK()` has side effects, so validation is not a pure predicate.

Test signals: constructing with invalid and valid URLs; repeated operations after mutating `Url`; lifecycle where shared `ecMsg` captures errors across calls.
