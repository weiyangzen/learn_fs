# sources/distributed-fs/xrootd/src/XrdOss/XrdOssDefaultSS.hh

## Purpose
Declares the external factory for obtaining the default OSS storage-system object.

## Important APIs, types, and functions
`XrdOssDefaultSS(XrdSysLogger *logger, const char *cfg_fn, XrdVersionInfo &urVer)` returns an `XrdOss *` for callers that want the default configured storage system. It requires a logger, an optional/required config path depending on the environment, and the caller's version info for compatibility checks.

## Control flow
The header has no implementation. Its documented call flow is: include the header, provide `XrdVERSIONINFODEF`/`XrdVersionInfo`, and call the factory. The implementation elsewhere is expected to configure and return an OSS object or null.

## State and persistence
No state is declared here. The returned object likely owns process-level storage-system configuration, but that is outside this file.

## Dependencies and integration points
Includes `XrdVersion.hh` and `XrdOss.hh`, so it bridges plugin/factory users to the OSS API. It is an ABI-facing declaration for code that loads or embeds the default storage system.

## Risks and test signals
Version compatibility and null-return handling are the main contract points. Tests should verify callers pass compatible version metadata and fail cleanly on missing or invalid configuration.
