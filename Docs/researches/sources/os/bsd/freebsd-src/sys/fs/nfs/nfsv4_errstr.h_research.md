# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsv4_errstr.h

`nfsv4_errstr.h` provides a small static mapping from NFSv4 protocol error values to human-readable strings.

Key contents:
- Defines `static const char *nfsv4_errstr[]`, indexed by `errval - NFSERR_BADHANDLE`, covering `NFSERR_BADHANDLE` through `NFSERR_XATTR2BIG`.
- Includes strings for core NFSv4 errors, NFSv4.1 session/pNFS errors, NFSv4.2 offload/layout errors, and extended attribute errors.
- Defines `static const char *nfsv4_geterrstr(int errval)`, which returns `NULL` if the error is outside the NFSv4 range and otherwise returns the static string.

Important integration points:
- The array size is tied to `NFSERR_XATTR2BIG - 10000`, so it depends on the contiguous NFSv4 error numbering in `nfsproto.h`.
- The header intentionally defines static storage in the including C file, with comments noting it is currently used narrowly rather than packaged as a separate library function.

Research notes:
- This is a user-facing diagnostic helper, likely for mount/client error reporting.
- Any new contiguous NFSv4 error added in `nfsproto.h` should be reflected here to keep indexing correct and messages meaningful.
