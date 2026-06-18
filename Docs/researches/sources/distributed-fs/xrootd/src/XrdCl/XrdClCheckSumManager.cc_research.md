# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.cc

## Purpose

This file implements `XrdCl::CheckSumManager`, the process-level registry and loader for checksum calculators. It pre-registers built-in `md5`, `crc32`, `crc32c`, and `adler32` calculators, dynamically loads other algorithms through `XrdCksLoader`, and can compute a checksum over a local file.

## Important APIs, types, and functions

The constructor creates an `XrdCksLoader` using the client version info and inserts built-in calculator prototypes into `pCalculators`. The destructor deletes all stored prototypes and the loader.

`GetCalculator(const std::string&)` locks `pMutex`, looks up the algorithm prototype, dynamically loads and caches a new prototype if missing, then returns `prototype->New()`. The caller owns the returned calculator.

`Calculate(XrdCksData&, const std::string&, const std::string&)` obtains a calculator, opens a local file with `open(O_RDONLY)`, reads it in 2 MiB blocks, updates the calculator, stores the final digest bytes into `XrdCksData`, and closes/cleans up.

## Control flow

Calculator lookup is lazy for non-built-in algorithms. A missing algorithm triggers loader lookup, logging, cache insertion on success, and a fresh calculator instance return. Local-file calculation is sequential: get calculator, open file, read/update until EOF, set result from final digest, cleanup.

## State and persistence behavior

`pCalculators` stores owned calculator prototypes for the life of the manager. The manager itself is normally a singleton-like object behind `DefaultEnv::GetCheckSumManager`. There is no durable persistence; the cache is process memory only.

## Dependencies and integration points

Dependencies include XRootD checksum classes (`XrdCksCalc`, `XrdCksLoader`, built-in calculator headers), logging/default environment, `XrdSysE2T`, mutex helpers, version macros, and POSIX `open/read/close`. It is used by `CheckSumHelper`, `Utils::GetLocalCheckSum`, and copy/checksum features across the client.

## Risks and edge cases

`Calculate` does not handle `read` returning `-1` after `EINTR` specially; it treats it as a hard error. It allocates the read buffer manually and closes the descriptor on read error and success, but there is no RAII for the fd. If `result.Set` does not copy digest bytes, it would depend on calculator lifetime; the surrounding XrdCks API is expected to copy.

`GetCalculator` logs dynamic loader errors using a fixed 1024-byte buffer. Algorithm names are case-sensitive at this layer; callers such as `CopyProcess::AddJob` lower-case checksum types for copy jobs. Returned calculators must be deleted by callers.

## Test signals

No direct tests are included. Indirect coverage comes from `xrdcp --cksum`, `xrdcp --cksrc`, local checksum utilities, ZIP CRC flows, and any tests around supported checksum type discovery. Good focused tests would verify built-in lookup, dynamic-load failure, local file success, read/open failure, and concurrent `GetCalculator` calls.
