<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh

## Purpose

`XrdOucUtils.hh` declares the static `XrdOucUtils` utility facade used by XRootD code for configuration parsing, filesystem setup, identity generation, size formatting, account lookup, URL encoding, and daemon/process helpers.

## Important APIs, Types, And Functions

- `pathMode` is the common directory mode for generated paths.
- Parsing APIs include `argList()`, `doIf()`, `parseLib()`, `parseHome()`, `mode2mask()`, and `Token()`.
- Conversion APIs include `bin2hex()`, `hex2bin()`, `fmtBytes()`, `genHumanSize()`, `HSize()`, `i2bstr()`, `Log2()`, `Log10()`, and `touint8_t()`.
- Filesystem/process APIs include `findPgm()`, `genPath()`, `getFile()`, `makeHome()`, `makePath()`, `ReLink()`, `subLogfn()`, `Undercover()`, `ValPath()`, `PidFile()`, and `getModificationTime()`.
- Account APIs include `getGID()`, `getUID()`, `GidName()`, `GroupName()`, `UidName()`, and `UserName()`.
- URL/text APIs include `Sanitize()`, `toLower()`, `trim()`, `UrlEncode()`, and `UrlDecode()`.

## Control Flow

The header exposes only static methods, so consumers do not need object lifetime management. Most routines return either boolean success, a byte/character count, `0` on success with negative errno-style failure, or a heap pointer on success. The declarations also reveal ownership-sensitive APIs: `genPath()` and `getFile()` return allocated buffers, while many routines require caller-supplied mutable buffers.

## State And Persistence

The header itself has no state, but it declares APIs whose implementation maintains process-global UID/GID caches and generated identity state. Several calls create or validate persistent filesystem objects and can change the process working directory or daemon state.

## Dependencies And Integration Points

The header uses `sys/types.h`, `sys/stat.h`, `string`, `string_view` via declarations, `unordered_set`, `vector`, and `cstdint`, plus forward declarations for `XrdSysError`, `XrdOucString`, and `XrdOucStream`. It is a low-level dependency of configuration, startup, cache, HTTP, and logging code.

## Risks And Edge Cases

- Return conventions are mixed: some functions return negative errno, some positive errno, some `false`, and some null pointers.
- Ownership is not encoded in types for allocated `char*` results.
- Many APIs predate modern C++ string types and expose raw buffers with caller-provided lengths.
- `touint8_t()` can throw exceptions unlike most other utilities, which use error codes or logging.

## Test Signals

Header-level tests are mostly compile and contract tests: include it from C++17 translation units, verify declaration availability for `std::string_view`, check overload resolution for `trim`, and exercise representative APIs for return convention documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUtils.hh -->
