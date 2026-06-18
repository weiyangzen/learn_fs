# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileSystemUtils.cc

## Purpose
`XrdClFileSystemUtils.cc` implements utility behavior outside the core `FileSystem` class, currently focused on aggregating space information across all disk servers that host a path.

## Important APIs, Types, And Functions
`FileSystemUtils::SpaceInfoImpl` stores total, free, used, and largest-free-chunk counters. `SpaceInfo` constructors/destructor and getters expose those counters. `FileSystemUtils::GetSpaceInfo` performs the main workflow: deep-locate the path with `OpenFlags::Compress | OpenFlags::PrefName`, query every returned server with `QueryCode::Space`, parse the response as CGI parameters, aggregate `oss.space`, `oss.free`, and `oss.used`, and take the maximum `oss.maxf`.

## Control Flow
The function first calls `fs->DeepLocate`; non-OK status aborts. It preserves `suPartial` from deep locate and wraps the returned `LocationInfo` in `unique_ptr`. For each location, it constructs a temporary `FileSystem`, queries `QueryCode::Space` with the original path as a `Buffer`, wraps the response buffer, constructs a fake URL to reuse `URL` CGI parsing, and validates every expected parameter. A successful pass creates a new `SpaceInfo` and returns OK or partial.

## State And Persistence Behavior
There is no durable state. `result` is assigned a newly allocated `SpaceInfo` on success and remains caller-owned. Temporary buffers and location lists are managed by `unique_ptr` to prevent leaks on early returns after acquisition.

## Dependencies And Integration Points
The implementation depends on `FileSystem`, `LocationInfo`, `Buffer`, `URL`, and XRootD query semantics for `oss.space`, `oss.free`, `oss.used`, and `oss.maxf`.

## Risks And Test Signals
Risks include invalid or missing CGI keys, numeric conversion errors, partial deep-locate behavior, and early abort on one failed server query. Tests should include multi-server aggregation, max-free-chunk maximum behavior, malformed values with trailing characters, missing parameters, zero-location locate responses, and propagation of `suPartial`.
