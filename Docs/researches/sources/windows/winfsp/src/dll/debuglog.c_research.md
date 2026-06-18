# File Research: sources/windows/winfsp/src/dll/debuglog.c

Human-readable trace logging for WinFsp request/response traffic and filesystem metadata.

Key responsibilities:
- Maintains a global debug log handle set by `FspDebugLogSetHandle`.
- Emits formatted debug text to the configured file handle or `OutputDebugStringA`.
- Provides helpers for logging security descriptors, SIDs, `FILETIME`, file info, volume info, wide-char buffers, user contexts, and reparse data.
- Logs every major `FSP_FSCTL_TRANSACT_REQ` kind in `FspDebugLogRequest`.
- Logs every major `FSP_FSCTL_TRANSACT_RSP` kind in `FspDebugLogResponse`.
- Decodes create dispositions, create/open flags, access tokens, file names, EA/security payloads, query directory markers, FSCTL reparse operations, volume labels, and stream/security operations.

Important behavior:
- Skips response logging for `STATUS_PENDING`.
- Uses `FspDiagIdent()` and the current thread ID in trace prefixes.
- Converts security descriptors to SDDL when present.
- Handles mount-point, symlink, Microsoft, and GUID reparse payload shapes.
- Uses fixed-size stack buffers with truncation-oriented formatting.

Dependencies:
- Includes `dll/library.h`, `sddl.h`, and `stdarg.h`.
- Depends on WinFsp transaction structures and Windows APIs such as `ConvertSecurityDescriptorToStringSecurityDescriptorA`, `ConvertSidToStringSidA`, `FileTimeToSystemTime`, `WriteFile`, and `OutputDebugStringA`.

Notable risks:
- Formatting is intentionally diagnostic and uses Windows `wvsprintf/wsprintf` style APIs with fixed buffers.
- Logs can expose paths, security descriptors, access tokens, and user context pointers; this should remain a debug facility.
