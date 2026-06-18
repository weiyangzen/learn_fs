# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/saunafs/saunafs_error_codes.h

Purpose: this header defines the SaunaFS metadata/client error code namespace and declares `saunafs_error_string(uint8_t status)`.

Important APIs and types: `enum saunafs_error_code` maps numeric statuses from `SAUNAFS_STATUS_OK` through filesystem, metadata, chunk, quota, session, lock, range, timeout, and parsing failures. Codes include POSIX-like cases (`EPERM`, `ENOENT`, `EACCES`, `EEXIST`, `EINVAL`, `ENOTEMPTY`, `ENOSPACE`, `EROFS`, `ENAMETOOLONG`, `EFBIG`, `EBADF`, `ENODATA`, `E2BIG`) and SaunaFS-specific cases (`CHUNKLOST`, `NOCHUNKSERVERS`, `WRONGCHUNKID`, `BADMETADATACHECKSUM`, `METADATAVERSIONMISMATCH`, `WAITING`). `SAUNAFS_ERROR_MAX` is a sentinel.

Control flow and state: callers receive or store compact integer statuses, pass them to string/conversion functions, then translate to FSAL/NFS errors in higher layers. The header has no mutable state.

Dependencies and integration points: FSAL_SAUNAFS uses this status space through the C API and `saunafs_internal.c`. The enum is part of the boundary between SaunaFS client semantics and Ganesha's `fsal_status_t`/NFSv4 status mapping.

Risks: numeric stability matters because errors may cross C ABI boundaries. New SaunaFS errors require updates in conversion code or they may collapse to generic errors. Some codes are semantically close but not equivalent (`DELAYED`, `WAITING`, `TEMP_NOTPOSSIBLE`, `NOTDONE`), so retry/delay behavior must be checked in callers.

Test signals: verify every enum value is accepted by `saunafs_error_string`, `sau_error_conv`, and FSAL conversion paths; include unknown/out-of-range values and retry-like statuses.
