# sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.hh

## Purpose
`XrdClUtils.hh` declares the XrdCl utility namespace class and small RAII helpers used across the client. It exposes shared helper APIs for parameter lookup, address resolution, checksum handling, TPC/EC/protocol capability checks, config parsing, logging, and chunk splitting.

## Important APIs, Types, And Functions
- `class Utils` is a static-method utility class with no instance state.
- `Utils::splitString` forwards to `XrdOucTUtils::splitString`, keeping XrdCl and XrdHttp on a shared split implementation.
- `enum AddressType` encodes `IPAuto`, `IPAll`, `IPv6`, `IPv4`, and `IPv4Mapped6`.
- Inline capability methods `GetProtocolVersion`, `HasXAttr`, `HasKSameFS`, and `HasPgRW` query the active transport through `DefaultEnv::GetPostMaster()->QueryTransport`.
- `Utils::SplitChunks` uses `ChunkList`/`ChunkInfo` from `XrdClXRootDResponses.hh`.
- `ScopedDescriptor` closes a POSIX file descriptor on destruction unless released.
- Linux-only `ScopedFsUidSetter` temporarily sets filesystem UID/GID with `setfsuid`/`setfsgid` and restores previous values in the destructor.

## Control Flow
The header is mostly declarations plus small inline helpers. `GetProtocolVersion` queries a transport property into an `AnyObject`, extracts a heap-allocated `int`, writes the output parameter, deletes the temporary, and returns transport status. Capability helpers short-circuit local files where appropriate and compare protocol versions to constants such as `kXR_PROTXATTVERSION`, `kXR_PROTCLONEVERSION`, and `kXR_PROTPGRWVERSION`. RAII helper destructors release OS-level state automatically.

## State And Persistence Behavior
`Utils` itself is stateless. `ScopedDescriptor` owns one integer descriptor until `Release()`. `ScopedFsUidSetter` stores requested UID/GID, previous UID/GID, stream name, and an `IsOk()` flag. The fsuid/fsgid changes affect the current process/thread filesystem credential state while the object is alive on Linux, so construction and destruction timing is significant.

## Dependencies And Integration Points
The header pulls in core XrdCl types (`Status`, `Log`, `URL`, `PropertyList`, `DefaultEnv`, `PostMaster`, `XRootDTransport`, `ChunkList`, `Message`) plus XrdNet and XrdOuc helpers. It is included by copy sources (`XrdClXCpSrc.cc`), response parsing, message handling, and other XrdCl modules needing common utilities.

## Risks And Edge Cases
- `ScopedFsUidSetter` calls `setfsuid`/`setfsgid` twice to verify state and can leave partial changes if one setter succeeds and the other fails before destruction restores only recorded previous values.
- `GetProtocolVersion` returns an OK status even when `AnyObject` does not contain an `int`; callers then see the unchanged `protver`.
- `HasPgRW` returns false for local files even though other capabilities return true locally; this distinction matters for page read/write copy logic.
- The header includes many dependencies, so changes here can increase rebuild cost and coupling.

## Test Signals
Compile-time tests should cover Linux and non-Linux builds, protocol-version thresholds, missing transport query data, local-file short-circuits, `ScopedDescriptor::Release()`, and fsuid/fsgid restore behavior in privileged or mocked environments.
