<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc

## Purpose

`XrdOucUtils.cc` implements a broad set of process, path, parsing, identity, formatting, URL, and filesystem utility routines used throughout XRootD. It is the implementation behind the static `XrdOucUtils` facade and also defines a few free helper functions used by URL/auth sanitization paths.

## Important APIs, Types, And Functions

- Anonymous `idInfo`, `gidMap`, `uidMap`, `AddID()`, and `LookUp()` implement TTL-cached UID/GID name lookup guarded by `XrdSysMutex`.
- `argList()`, `Token()`, `is1of()`, `doIf()`, `parseLib()`, and `parseHome()` support configuration parsing.
- `bin2hex()`, `hex2bin()`, `i2bstr()`, `Log2()`, `Log10()`, `fmtBytes()`, `HSize()`, and `genHumanSize()` provide text/binary/size conversions.
- `getFile()`, `findPgm()`, `getGID()`, `getUID()`, `GidName()`, `UidName()`, `GroupName()`, and `UserName()` wrap common POSIX filesystem and account queries.
- `genPath()`, `makeHome()`, `makePath()`, `mode2mask()`, `ReLink()`, `subLogfn()`, `ValPath()`, `PidFile()`, and `getModificationTime()` manipulate paths and persistent filesystem artifacts.
- `Ident()` and local `genSID()` derive a server identity string and 48-bit fingerprint from host, port, program, instance, site, SHA3, and CRC32C.
- `Undercover()` daemonizes on non-Windows platforms by double-forking, creating a new session, redirecting descriptors to `/dev/null`, and optionally reporting status through a pipe.
- `UrlEncode()`, `UrlDecode()`, `obfuscateAuth()`, `stripCgi()`, and `splitHostCgi()` support HTTP/query-string handling and secret redaction.

## Control Flow

Most functions are independent static utilities. Configuration helpers consume tokens from `XrdOucStream` in place: `doIf()` evaluates host, environment, executable, and instance-name predicates; `parseLib()` reads a plugin path and optional trailing parameters; `parseHome()` validates an absolute home path plus an optional `group` modifier. Filesystem helpers either return negative errno values or emit messages through `XrdSysError`.

Identity generation is lazy-static: `Ident()` initializes `theSID` once through `genSID()`, then formats per-call user/process/site details around that process-global fingerprint. The URL redaction helpers scan strings for CGI or authorization token patterns and rewrite only selected token values, leaving other query content intact.

## State And Persistence

The UID/GID caches are process-global maps with TTL expiration and heap-owned strings. `Ident()` stores static process identity state after first use. `makeHome()`, `makePath()`, `ReLink()`, `PidFile()`, and `Undercover()` persistently affect directories, symlinks, pid files, working directory, process session, and file descriptors. `getFile()` returns a heap buffer that callers must free; `genPath()` and parts of version/path handling also return `strdup()` memory.

## Dependencies And Integration Points

This file depends on POSIX account and filesystem APIs, `XrdNetUtils`, `XrdOucCRC`, `XrdOucSHA3`, `XrdOucStream`, `XrdOucString`, `XrdOucEnv`, `XrdSysError`, `XrdSysE2T`, `XrdSysMutex`, and platform wrappers. It is a shared support layer for config parsers, daemon startup, logging path setup, auth redaction, and path validation in many XRootD components.

## Risks And Edge Cases

- Several APIs mutate input buffers in place (`argList`, `makePath`, `subLogfn`, `Sanitize`) and require caller-owned writable memory.
- `genPath(const char*, const char*, const char*)` uses a fixed 2048-byte stack buffer and unchecked `strcat()` after the initial copy.
- `argList()` supports simple quotes but not escapes; malformed quotes return `-EINVAL`.
- `a UID/GID` cache insertion keeps the first value until TTL expiration and ignores later updates for the same id.
- `touint8_t()` returns `static_cast<unsigned short>` from a `uint8_t` function and does not check for unconsumed trailing characters after `from_chars`.
- `obfuscateAuth()` has a static POSIX regex whose initialization can throw during first use.
- `stripCgi()` removes token-character runs after a key but does not fully parse query separators, so unusual CGI syntax can leave doubled separators.

## Test Signals

Useful tests should cover malformed quoted argument lists, odd-length and invalid hex decoding, `doIf()` branches for host/defined/exec/named predicates, path creation with existing directories and reset mode, UID/GID cache expiry, URL encode/decode round trips, authorization redaction for bearer and `authz=` forms, `stripCgi()` at first/middle/last query positions, daemonization pipe status behavior, and `Ident()` stability for repeated calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.cc -->
