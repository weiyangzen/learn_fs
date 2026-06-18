# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsv4_errstr.h

This small header provides static string descriptions for NFSv4 errors from `NFSERR_BADHANDLE` through `NFSERR_CBPATHDOWN`, plus a helper for mapping an error value to one of those strings.

Key contents:
- Static array `nfsv4_errstr[48]` with human-readable messages for the contiguous NFSv4 error range starting at `NFSERR_BADHANDLE`.
- Static helper `nfsv4_geterrstr(int errval)`, which returns `NULL` if the value is outside `NFSERR_BADHANDLE` through `NFSERR_CBPATHDOWN`, otherwise indexes the array by subtracting `NFSERR_BADHANDLE`.

Important behavior:
- The header intentionally defines static storage directly because it is only expected to be used in a small number of C files.
- The array only covers NFSv4.0-era errors through callback-path-down. NFSv4.1 errors defined later in `nfsproto.h` are not included.
- Correctness depends on the NFSv4 error values being contiguous across this range.

Research notes:
- This is diagnostic/UI support, not core protocol handling.
- If adding new error strings, the range check and array size must be updated together.
