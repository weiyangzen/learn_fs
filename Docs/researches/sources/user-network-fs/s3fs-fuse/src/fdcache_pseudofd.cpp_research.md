# sources/user-network-fs/s3fs-fuse/src/fdcache_pseudofd.cpp

Purpose: Implements the singleton `PseudoFdManager`, which allocates small integer pseudo-fds used by s3fs instead of exposing raw physical cache fds.

Important APIs and functions: Static `Get` allocates a pseudo-fd; static `Release` releases it. Internals include `GetManager`, `GetUnusedMinPseudoFd`, `CreatePseudoFd`, and `ReleasePseudoFd`.

Control flow: Allocation locks `pseudofd_list_lock`, finds the smallest unused integer starting at 2, pushes it into `pseudofd_list`, sorts the vector, and returns it. Release locks, linearly searches, erases a matching value, and reports success/failure.

State and persistence behavior: Process-local only; no persistence. The minimum starts at 2 to avoid confusion with standard descriptors 0 and 1.

Dependencies and integration points: Used by `PseudoFdInfo` construction, reset, and destruction. Indirectly used by `FdEntity` and `AutoFdEntity` for all open handles.

Risks: Allocation is O(n log n) due to sort after every push and linear scans, though open pseudo-fd counts are likely small. Pseudo-fds are process-global, not per-entity, so leaks in any entity can exhaust or inflate the vector.

Test signals: Indirect coverage through open/dup/close integration tests. A targeted unit test could verify reuse of released low-number pseudo-fds and release-failure behavior.
