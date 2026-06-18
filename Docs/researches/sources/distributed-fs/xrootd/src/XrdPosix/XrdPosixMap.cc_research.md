## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixMap.cc

Purpose: implements translation between XRootD client/protocol metadata/status and POSIX modes, stat buffers, access modes, `errno`, and return values.

Important APIs/functions: `Flags2Mode`, `Entry2Buf`, private `mapCode`, `Mode2Access`, and `Result`.

Control flow: `Flags2Mode()` maps `XrdCl::StatInfo` flags to `S_IF*` and user permission bits, plus special XRootD SFS flags through `st_rdev`. `Entry2Buf()` maps directory-list stat info into `struct stat`, preserving extended POSIX permission mode when available or widening owner bits to other bits when not. `mapCode()` maps `XrdCl` client error codes to errno values. `Result()` handles success, protocol error responses via `XProtocol::toErrno`, generic client errors through `mapCode`, stores the message into `ecMsg`, sets `errno`, and returns either `-1` or `-errno`.

State and persistence: only static `Debug` flag. No durable state.

Dependencies/integration: uses `XrdCl` status/stat/list types, `XProtocol`, `XrdSfsFlags`, `XrdOucECMsg`, and system `stat` flags. It is used throughout admin, file, directory, and wrapper layers.

Risks: errno mapping choices affect all POSIX semantics and may not match caller expectations, for example `errNotFound` to `EIDRM`. `Entry2Buf()` sets `st_dev=1` to avoid offline translation side effects, which is protocol-coupled. `st_blocks` overcount issue appears here too. `mapError` is declared in the header but not defined/used.

Test signals: exhaustive status-code mapping tests; extended/non-extended stat conversion; directory entry without stat info returns `EIO`; mode-to-access mapping for all permission bits.
