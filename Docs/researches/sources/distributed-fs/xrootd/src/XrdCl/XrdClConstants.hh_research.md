# sources/distributed-fs/xrootd/src/XrdCl/XrdClConstants.hh

## Purpose

This header centralizes XrdCl log mask constants and default environment values. It defines default numeric and string settings used by connection management, copy behavior, TLS behavior, metalink handling, retry policies, checksums, and plugin configuration.

## Important APIs, types, and functions

Log masks include `AppMsg`, `UtilityMsg`, `FileMsg`, `PollerMsg`, `PostMasterMsg`, `XRootDTransportMsg`, `TaskMgrMsg`, `XRootDMsg`, `FileSystemMsg`, `AsyncSockMsg`, `JobMgrMsg`, `PlugInMgrMsg`, `ExDbgMsg`, `TlsMsg`, and `ZipMsg`.

Default integers include connection and stream timeouts, retry counts, copy chunk settings (`DefaultCPChunkSize`, `DefaultCPParallelChunks`, `DefaultCPInitTimeout`, `DefaultCPTPCTimeout`, `DefaultCPTimeout`), xcp block size, TCP keepalive settings, metalink settings, TLS toggles, write recovery retry limit, copy retry count, and page read/write default.

Default strings include poller preference, network stack, monitor settings, plugin paths, recovery toggles, redirector defaults, TLS debug level, client config paths, copy target symlink, and copy retry policy.

`to_lower(std::string)` lower-cases a key. `theDefaultInts` and `theDefaultStrs` map lower-cased environment variable names to default values.

## Control flow

`DefaultEnv` consumes these constants and maps during environment initialization. Command-line tools and copy jobs then query `DefaultEnv::GetEnv()` for mutable runtime values, falling back to these defaults.

## State and persistence behavior

The constants are compile-time defaults. The two `static std::unordered_map` objects are header-defined internal-linkage maps in each translation unit that includes the header. Runtime environment overrides live elsewhere in `Env`; this header does not persist state.

## Dependencies and integration points

Dependencies include `<cstdint>`, `<unordered_map>`, `<string>`, and `<algorithm>`. Integration is broad: `DefaultEnv`, `CopyProcess`, `ClassicCopyJob`, `XrdClCopy.cc`, logging, TLS configuration, PostMaster, and file recovery code all rely on these names and defaults.

## Risks and edge cases

Defining non-const static maps in a header gives each translation unit its own copy. That avoids ODR conflicts because of internal linkage but increases initialization work and can hide divergence if code mutates a local copy. `to_lower` calls `::tolower` on `char` without unsigned conversion, which can be undefined for negative non-ASCII bytes.

New environment defaults must be added both as constants and to the correct map to be discoverable. Some defaults are used directly in code as fallback values, so inconsistent map registration can create split behavior.

## Test signals

Compile-time integration is extensive. Runtime tests should check that `DefaultEnv` registers expected defaults, CLI overrides replace them, and copy-related defaults (`CPChunkSize`, `CPParallelChunks`, `CpRetry`, `CpRetryPolicy`, `CpUsePgWrtRd`) flow into `CopyProcess` and `ClassicCopyJob`.
