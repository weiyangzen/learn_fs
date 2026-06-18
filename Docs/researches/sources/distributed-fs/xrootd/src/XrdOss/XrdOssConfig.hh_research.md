# sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.hh

## Purpose
Provides small shared configuration definitions for the OSS implementation: version string, success constant, option flags, dual-path records, and the structured argument used while constructing cache spaces.

## Important APIs, types, and functions
`XRDOSS_VERSION` is the OSS config version string. `XrdOssOK` normalizes success to zero. `XrdOss_USRPRTY` and `XrdOss_CacheFS` are flags stored in `XrdOssSys::OptFlags`. `OssDPath` is a linked-list node pairing logical and physical paths for stats reporting. `OssSpaceConfig` holds references to a space name, path, and mount name while parsing/building `oss.space`; it also carries booleans for XA path layout, mount-check failure handling, and whether mount checking is enabled.

## Control flow
The header has no executable control flow. Its objects are populated by `XrdOssConfig.cc`: `OssSpaceConfig` starts as XA-enabled, no-fail false, and no mount check, then `xspace()` mutates the flags before `xspaceBuild()` creates an `XrdOssCache_FS`.

## State and persistence
`OssDPath` owns duplicated path strings indirectly through its fields but has no destructor, matching process-lifetime config storage. `OssSpaceConfig` stores references to `XrdOucString` instances owned by the parser stack and is not persistent beyond build time.

## Dependencies and integration points
Forward-declares `XrdOucString` to avoid pulling the full string implementation into all users. Consumed primarily by `XrdOssConfig.cc`, with `OptFlags` values used by other OSS code to detect cache filesystem and user-priority staging behavior.

## Risks and test signals
The reference fields in `OssSpaceConfig` require stack-lifetime discipline. Tests should cover config paths that set `XrdOss_CacheFS`, `XrdOss_USRPRTY`, and `OssDPath` generation for stats, plus wildcard `oss.space` expansion that repeatedly reuses the same `OssSpaceConfig` object.
