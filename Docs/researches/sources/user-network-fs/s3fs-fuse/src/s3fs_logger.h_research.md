# sources/user-network-fs/s3fs-fuse/src/s3fs_logger.h

Purpose: declares `S3fsLog`, log levels, logging macros, and FUSE-context logging helpers used throughout s3fs-fuse.

Important APIs and types: `S3fsLog::Level` encodes CRIT/ERR/WARN/INFO/DBG as bit masks. Static helpers map levels to syslog priorities and string prefixes, provide timestamp text, select output/error streams, set/reopen log files, change level, and write atomic formatted output. Macros include `S3FS_PRN_EXIT`, `S3FS_PRN_CRIT`, `S3FS_PRN_ERR`, `S3FS_PRN_WARN`, `S3FS_PRN_INFO*`, `S3FS_PRN_DBG`, `S3FS_PRN_CURL`, `S3FS_PRN_CACHE`, and FUSE-context variants.

Control flow: call sites use macros, which first check the active log level and then pass file/function/line context to implementation functions. Exit/init/launch/cache/curl macros have specialized output behavior. FUSE macros append `pid`, `uid`, and `gid` when `fuse_get_context()` is available.

State and persistence: declares static logger process state but no per-call persistence. Macros may expose sensitive values unless callers mask them or `insecure_logging` intentionally disables masking in helper functions.

Dependencies and integration points: includes syslog, common globals, FUSE context APIs via call sites, and is included by nearly every module for diagnostics.

Risks: macro-heavy logging can evaluate varargs in surprising ways and couples call sites to global `foreground`/`instance_name`. Format strings are compile-checked on implementation functions but macro varargs still need care. Because logging is used in signal handlers, only async-signal-safe paths should be called from handlers, but current handlers call higher-level logging operations.

Test signals: compile with format warnings, exercise every macro at each level, verify FUSE-context suffixes, and verify sensitive values are masked at representative credential and IAM call sites.
