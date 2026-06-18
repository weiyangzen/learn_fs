# sources/distributed-fs/xrootd/src/XrdOss/XrdOssError.hh

## Purpose
Defines OSS-specific error-code numbers, mappings to system `errno` values, and human-readable text used by the OSS error table registered during configuration.

## Important APIs, types, and functions
`XRDOSS_EBASE` and `XRDOSS_ELAST` delimit the custom error range 8001 to 8028. `XRDOSS_E80xx` names individual OSS codes. `XRDOSS_N80xx` maps each custom code to a POSIX errno such as `EROFS`, `EPERM`, `EFBIG`, `EXDEV`, `ENOSPC`, or `EAGAIN`. `XRDOSS_T80xx` provides the message text used by `XrdOssErrorText` in `XrdOssConfig.cc`.

## Control flow
No executable control flow exists. `XrdOssSys::Configure()` constructs `XrdSysError_Table` and `XrdSysError_Table_Errno` from the text and errno mappings.

## State and persistence
No mutable state. The definitions are compile-time constants.

## Dependencies and integration points
Included by most OSS implementation files to return consistent negative OSS errors. The mappings are used by `XrdSysError` so callers can see both custom OSS diagnostics and conventional errno behavior.

## Risks and test signals
The range includes a commented-out `XRDOSS_E8016` while `XRDOSS_N8016` and text still exist; table ordering and array length must remain aligned with `XRDOSS_EBASE`. Tests should check every code maps to intended errno/text, especially remote storage response errors, creation-prohibited, relative-path, and dynamic-cast failures.
