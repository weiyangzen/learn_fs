# sources/user-network-fs/s3fs-fuse/src/fdcache_auto.h

Purpose: Declares the small RAII wrapper that protects `FdEntity` pseudo-fd reference accounting.

Important APIs and types: `AutoFdEntity` is non-copyable and non-movable. It exposes `Close`, `Detach`, `Attach`, `GetPseudoFd`, `Open`, `GetExistFdEntity`, and `OpenExistFdEntity`. It stores a raw `FdEntity*` and an integer pseudo-fd.

Control flow contract: Construct empty, call an open/attach method, use the returned entity and `GetPseudoFd`, then let the destructor or explicit `Close` release it. `Detach` is an escape hatch that transfers close responsibility to the caller.

State and persistence behavior: No direct persistence; the wrapped entity may persist page-list metadata and cache files when closed.

Dependencies and integration points: Includes `metaheader.h` and `filetimes.h`, forward-declares `FdEntity`, and provides a header-level wrapper for FUSE operation code.

Risks: Raw pointer plus pseudo-fd state is intentionally minimal but easy to misuse if detached pseudo-fds are not closed. The class prevents copying/moving to avoid double-close, but callers still need clear ownership after `Detach`.

Test signals: Indirectly covered by file operation tests that open, reopen, flush, release, and hit early errors.
