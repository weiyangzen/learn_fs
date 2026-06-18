## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.hh

Purpose: declares the static mapping utilities that convert XRootD client statuses and metadata into POSIX-facing values.

Important APIs/types: `XrdPosixMap::Flags2Mode`, `Entry2Buf`, `Mode2Access`, `Result`, and `SetDebug`.

Control flow: all functions are stateless static helpers except the debug flag. Callers provide protocol objects and receive POSIX return codes, stat fields, access modes, and `errno` side effects.

State and persistence: static `Debug` boolean only.

Dependencies/integration: includes `XrdClFileSystem.hh` and `XrdClXRootDResponses.hh`; forward-declares `XrdOucECMsg` and `struct stat`. Used across the XrdPosix implementation.

Risks: private `mapError(int)` is declared but has no implementation in the researched source, suggesting dead API or historical leftover. Because `Result()` sets global/thread `errno`, tests must isolate side effects.

Test signals: compile/link coverage for all declared functions; direct tests for `SetDebug`; callers expecting `-errno` versus `-1` return modes.
