# sources/distributed-fs/xrootd/src/XrdCl/XrdClUtils.cc

## Purpose
`XrdClUtils.cc` implements the static utility surface declared in `XrdClUtils.hh`. It centralizes environment/URL parameter lookup, DNS address resolution and logging, time/byte formatting, checksum discovery and calculation, third-party-copy capability probes, lightweight config parsing, erasure-coding redirect validation, checksum-type inference, and chunk-list splitting for the XRootD C++ client.

## Important APIs, Types, And Functions
- `Utils::GetIntParameter` and `Utils::GetStringParameter` read a default from `DefaultEnv::GetEnv()` and let URL CGI parameters named `XrdCl.<name>` override it.
- `Utils::String2AddressType`, `GetHostAddresses`, and `LogHostAddresses` translate user-facing address-family preferences into `XrdNetUtils::AddrOpts`, resolve `host:port`, order IPv4/IPv6 partitions using `PreferIPv4`, optionally shuffle each partition, and log formatted network addresses.
- `Utils::TimeToString`, `GetElapsedMicroSecs`, and `BytesToString` provide formatting helpers used by diagnostics and user output.
- `Utils::GetRemoteCheckSum`, `GetLocalCheckSum`, `GetSupportedCheckSums`, `NormalizeChecksum`, and `InferChecksumType` coordinate checksum query/calculation and choose an interoperable checksum type across local files, metalinks, ZIP extraction, and remote `root`/`xroot` endpoints.
- `Utils::CheckTPC` and `CheckTPCLite` query server config for third-party copy and TPC-lite support, returning `suDone`, `suPartial`, or an error/fatal status depending on response shape.
- `Utils::GetDirectoryEntries`, `ProcessConfig`, `ProcessConfigDir`, and `Trim` provide small configuration-file helpers for `.conf` key-value input.
- `Utils::LogPropertyList` obfuscates sensitive values through `obfuscateAuth` before dump-level logging.
- `Utils::CheckEC` validates erasure-coded redirects behind `WITH_XRDEC`.
- `Utils::SplitChunks` breaks large `ChunkInfo` entries and/or long `ChunkList`s into bounded lists according to maximum chunk size and count.

## Control Flow
Most functions are single-purpose, synchronous helpers. Network-facing calls construct a `FileSystem`, `Buffer`, or `URL`, perform an XRootD query, validate the shape of the response, and translate malformed or unsupported responses into `XRootDStatus`/`Status`. `InferChecksumType` builds source and destination capability lists, gives local endpoints a fixed supported set, optionally extracts metalink/ZIP-supported checksums, and returns the first compatible type. `SplitChunks` walks an input `ChunkList`, starts a new output list when `maxc` is reached, and slices an in-progress `ChunkInfo` when its remaining length exceeds `maxcs`.

## State And Persistence Behavior
This file does not persist durable state. It reads global client environment values such as `PreferIPv4`, `IPNoShuffle`, `ZipMtlnCksum`, and checksum-manager state from `DefaultEnv`. `ProcessConfig` clears and repopulates the caller-provided map; `ProcessConfigDir` repeatedly calls `ProcessConfig`, so a later valid file replaces previously loaded entries because `ProcessConfig` clears the map on each file. DNS shuffling uses a static random engine seeded from system time. Output parameters carry results for address vectors, checksum strings, config maps, and chunk-list vectors.

## Dependencies And Integration Points
The implementation depends on `XrdClFileSystem`, `DefaultEnv`, `CheckSumManager`, `RedirectorRegistry`, `Message`, `Optimizers`, `XrdNetUtils`, `XrdNetAddr`, `XrdOucTUtils`, and XRootD protocol constants. It integrates with copy/checksum code, transport capability checks through `DefaultEnv::GetPostMaster()` in inline functions from the header, logging via `DefaultEnv::GetLog()`, and metalink redirector state through `RedirectorRegistry::Instance()`.

## Risks And Edge Cases
- `ProcessConfigDir` can unintentionally discard earlier parsed config entries because every `ProcessConfig` call clears `config`.
- `LogHostAddresses` erases the last comma without guarding an empty address vector, so callers must only log non-empty results.
- `NormalizeChecksum` strips leading zeroes for `adler32` and `crc32`; downstream comparisons must use normalized forms.
- Remote checksum parsing assumes exactly two whitespace-separated fields and matching type names.
- `CheckEC` uses `std::stoul` on URL parameters under `WITH_XRDEC`; malformed numeric CGI values can throw unless caught higher up.
- DNS order and shuffle behavior is environment-dependent, which can make connection selection nondeterministic unless `IPNoShuffle` is enabled.

## Test Signals
Useful coverage includes URL CGI override precedence, address-family option selection and no-shuffle behavior, malformed checksum/config responses, TPC/TPC-lite query responses including empty and partial support cases, EC redirect parameter validation, local/remote/ZIP checksum inference matrices, and `SplitChunks` boundaries for `maxcs`, `maxc`, zero-length inputs, and buffer pointer advancement.
