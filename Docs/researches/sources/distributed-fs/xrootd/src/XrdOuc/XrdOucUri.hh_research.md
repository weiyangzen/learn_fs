# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.hh

Purpose: declares the static URI percent-encoding and decoding helper.

Important APIs, types, and functions: `Decode(const char*, int, char*)`, `Encode(const char*, int, char**)`, `Encode(const char*, int, char*)`, and `Encoded(const char*, int)` form the complete API. The class has no stateful behavior.

Control flow: callers either precompute size with `Encoded()` and encode into their own buffer, or use the allocating `Encode()` variant and free the returned buffer. Decoding writes into a caller buffer at least as large as the source plus null.

State and persistence: no object state exists. Allocating encode transfers heap ownership to the caller.

Dependencies and integration points: the header is standalone and documents the two-clause FreeBSD origin. It is used wherever XRootD needs percent-encoding without bringing in a larger URI library.

Risks and test signals: length parameters are explicit `int`, so callers must pass valid non-negative lengths. Tests should verify header/API use from C++ code, buffer sizing, and round-trips with the implementation.
