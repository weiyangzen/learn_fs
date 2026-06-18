<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c

## Purpose

This file provides common pNFS helpers for FSALs implementing metadata server or data server behavior. It focuses on XDR encoding of device IDs, network addresses, files layouts, flex file layouts, device address versions, and POSIX-to-NFSv4 error mapping.

## Important APIs, Types, and Functions

- Global `struct fsal_module *pnfs_fsal[FSAL_ID_COUNT]`: registry-like array for pNFS-capable FSALs.
- `xdr_fsal_deviceid`: encodes/decodes a 16-byte pNFS device ID as opaque bytes.
- `FSAL_encode_ipv4_netaddr`: encodes `netaddr4` protocol strings and universal IPv4 address strings for TCP, UDP, SCTP, and RDMA.
- `make_file_handle_ds`: creates a Ganesha DS-marked NFSv4 file handle from a lower FSAL opaque handle and server ID.
- `FSAL_encode_file_layout`: encodes `nfsv4_1_file_layout4` location body pieces and DS file handles.
- `FSAL_encode_v4_multipath`: encodes a multipath list of network endpoints.
- `FSAL_encode_data_server` and `FSAL_encode_flex_file_layout`: encode flex file data server and layout structures.
- `FSAL_encode_ff_device_versions4`: encodes flex file device address version and connection details.
- `posix2nfs4_error`: maps selected `errno` values to NFSv4 status values.

## Control Flow

The encoding helpers are linear XDR writers. Each writes one field or counted array at a time, logs a major/critical message on encoding failure or invalid input, and returns an NFSv4 status immediately. File handle helpers build temporary `nfs_fh4` buffers, mark them as DS handles, and encode them as byte arrays. Flex file layout encoding nests mirror and stripe loops and reuses `FSAL_encode_data_server`.

## State and Persistence Behavior

The helpers do not persist state beyond the global `pnfs_fsal` array. Encoded layouts persist only in the caller-provided XDR stream. Temporary file handle buffers are stack-local.

## Dependencies and Integration Points

The file depends on ONC RPC XDR functions, NFSv4 generated XDR routines, Ganesha file-handle layout (`file_handle_v4_t`), pNFS utility types, export/file-handle headers, and logging. FSALs call these helpers while servicing `LAYOUTGET`, `GETDEVICEINFO`, or flex-file layout operations.

## Risks and Edge Cases

- `FSAL_encode_ipv4_netaddr` only supports IPv4-style universal addresses and a fixed set of protocol numbers.
- `make_file_handle_ds` must fit lower opaque handles into `NFS4_FHSIZE`; oversize handles return server fault.
- Several XDR calls cast away constness; callers must pass stable values.
- `FSAL_encode_flex_file_layout` overwrites `nfs_status` in nested loops and returns the last status, relying on helpers to return immediately for most failures.
- `posix2nfs4_error` defaults unknown errors to `NFS4ERR_SERVERFAULT`.

## Test Signals

Tests should decode encoded netaddr strings for supported protocols, reject invalid protocols, verify DS file handle flags/server IDs/endian flags, exercise same-FH and per-stripe FH layout encoding, cover flex file mirrors/stripes, force oversize handle failure, and validate errno-to-NFSv4 status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/common_pnfs.c -->
