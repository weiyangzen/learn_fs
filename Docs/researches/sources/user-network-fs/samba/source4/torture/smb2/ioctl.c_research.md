# sources/user-network-fs/samba/source4/torture/smb2/ioctl.c

## Purpose

`ioctl.c` defines Samba's SMB2 torture suite for filesystem-control IOCTL behavior. It drives live SMB2 sessions against a test share and validates server behavior for FSCTL calls including shadow-copy enumeration, server-side copy resume keys, `FSCTL_SRV_COPYCHUNK`/`FSCTL_SRV_COPYCHUNK_WRITE`, compression state, network-interface enumeration, sparse files, allocated-range queries, zero-data hole punching, file-level trim, duplicate extents/reflink behavior, alternate data streams, and several Samba regression bugs.

The file is test code rather than production server code. Its persistent effects are temporary files/directories on the target SMB share, mostly `testfsctl.dat`, `testfsctl2.dat`, and `testfsctl_dir`, plus several regression-specific names. The suite is registered by `torture_smb2_ioctl_init()` as the `SMB2-IOCTL tests` suite.

## Important APIs, Types, and Helpers

- SMB2 client/torture APIs: `smb2_ioctl()`, `smb2cli_ioctl()`, async `smb2_ioctl_send()`/`smb2_ioctl_recv()`, `smb2_create()`, `smb2_read()`, `smb2_util_write()`, `smb2_util_close()`, `smb2_lock()`, `smb2_getinfo_file()`, `smb2_getinfo_fs()`, `smb2_setinfo_file()`, `torture_smb2_connection()`, `torture_smb2_tree_connect()`, `torture_smb2_testfile()`, and `torture_smb2_testdir()`.
- IOCTL request containers: `union smb_ioctl` and `struct smb2_ioctl`, always configured with `RAW_IOCTL_SMB2`, `SMB2_IOCTL_FLAG_IS_FSCTL`, the target `struct smb2_handle`, an FSCTL function code, input/output blobs, and `max_output_response`.
- NDR structures from `ndr_ioctl.h`: `req_resume_key_rsp`, `srv_copychunk_copy`, `srv_copychunk`, `srv_copychunk_rsp`, `compression_state`, `fsctl_net_iface_info`, `file_alloced_range_buf`, `file_zero_data_info`, `fsctl_file_level_trim_req`, `fsctl_file_level_trim_rsp`, `file_level_trim_range`, and `fsctl_dup_extents_to_file`.
- Feature probes: `test_ioctl_compress_fs_supported()`, `test_ioctl_fs_supported()`, and `test_ioctl_trim_supported()` query filesystem attributes or sector-size information before running capability-dependent tests.
- Shared data helpers: `patt_hash()`, `write_pattern()`, `check_pattern()`, and `check_zero()` write/read deterministic 64-bit offset patterns or zero-filled ranges in chunks, making later clone, punch, and sparse assertions precise.
- Shared setup helpers: `test_setup_open()`, `test_setup_create_fill()`, `test_setup_copy_chunk()`, `test_setup_trim()`, and `test_setup_dup_extents()` centralize file creation, file filling, resume-key acquisition, and IOCTL request initialization.

## Control Flow

Most tests follow the same shape: create or reopen one or two files, optionally probe server capability, construct a typed FSCTL payload with NDR push helpers, call `smb2_ioctl()` or `smb2cli_ioctl()`, assert the expected `NTSTATUS`, decode any output with NDR pull helpers, verify file size/data/attributes, then close handles and free temporary talloc contexts.

The copychunk block first validates `FSCTL_SRV_REQUEST_RESUME_KEY`, then exercises `FSCTL_SRV_COPYCHUNK` in simple, multi-chunk, tiny, overwrite, append, limit, lock-conflict, bad-key, same-file, overlapping same-file, permission, source-overrun, sparse-destination, undersized-output, zero-length, stream, and cross-share variants. `test_setup_copy_chunk()` is central: it creates/fills source and destination files, requests a resume key from the source handle, prepares the destination `FSCTL_SRV_COPYCHUNK` request, and fills `srv_copychunk_copy.source_key`.

Compression tests wrap `FSCTL_GET_COMPRESSION` and `FSCTL_SET_COMPRESSION`. They verify file flags, directory inheritance, invalid formats and buffers, `FILE_ATTRIBUTE_COMPRESSED` query behavior, create-time compressed attributes, `NTCREATEX_OPTIONS_NO_COMPRESSION`, attempts to set compression through `SMB2_SETINFO_FILE`, permission behavior, and not-supported filesystem behavior.

Sparse and zero-data tests wrap `FSCTL_SET_SPARSE`, `FSCTL_QUERY_ALLOCATED_RANGES`, and `FSCTL_SET_ZERO_DATA`. They validate sparse attribute toggling, ignored create-time sparse attributes, directory rejection, no-buffer and oversized sparse requests, allocated-range parsing and truncation, malformed query inputs, hole punching, filesystem-specific deallocation behavior, compressed+sparse interactions, copychunk of sparse ranges, invalid zero-data/QAR ranges, permission matrices, byte-range lock behavior, off-by-one cases, multi-range responses, and integer-overflow rejection.

Trim and duplicate-extents tests are capability gated. `FSCTL_FILE_LEVEL_TRIM` verifies sector-size trim support and that trimmed ranges do not corrupt untrimmed data. `FSCTL_DUP_EXTENTS_TO_FILE` validates reflink-like extent duplication, source/destination length boundaries, zero-byte requests, sparse and compressed combinations, same-file non-overlap success, same-file overlap rejection, bad handles, and the contrast with copychunk where byte-range locks do not block duplicate extents.

The regression tests target specific historical bugs. Bug 14607 uses a Samba torture FSCTL and checks response padding. Bug 14769 sends an async IOCTL then a close to ensure close waits for IOCTL completion. Bug 14788 validates `FSCTL_VALIDATE_NEGOTIATE_INFO` and `FSCTL_QUERY_NETWORK_INTERFACE_INFO` on normal and no-permission tree connects. Bug 15644 checks bad copychunk resume-key handling without a source handle.

## State and Persistence Behavior

The suite mutates only remote SMB share state and transient client memory. It creates, overwrites, truncates, extends, sparsifies, compresses, trims, clones, locks, unlocks, and deletes test files/directories. Most tests clean up by closing handles, unlinking files, calling `smb2_deltree()` for `DNAME`, or disconnecting extra tree connections. Some early-failure paths rely on the torture framework and later setup calls to clean existing names via `smb2_util_unlink()` or `smb2_deltree()`.

File contents are intentionally stateful within each test. Pattern data encodes logical offsets, so the tests can distinguish copied source data, appended duplicate data, overwritten data, sparse zero ranges, and untouched destination ranges. Several tests deliberately change file attributes such as sparse/compressed and then re-open the file to verify that the server persisted the attribute or that an unsupported create-time attribute was discarded.

## Dependencies and Integration Points

This file depends on Samba's generated NDR IOCTL bindings, SMB2 raw client layer, torture assertion framework, talloc memory ownership, cmdline credentials, loadparm/resolve configuration, and tevent request helpers. It integrates with the broader torture runner through `torture_smb2_ioctl_init()`, where every local static test is registered under a stable test name.

It also depends heavily on server and filesystem capabilities. Compression tests branch on `FILE_FILE_COMPRESSION`; sparse tests branch on `FILE_SUPPORTS_SPARSE_FILES`; duplicate-extents tests branch on `FILE_SUPPORTS_BLOCK_REFCOUNTING`; trim tests branch on `QFS_SSINFO_FLAGS_TRIM_ENABLED`; network interface tests require `SMB2_CAP_MULTI_CHANNEL`; SMB3 negotiate regression tests require protocol at least SMB 3.0 and a configured `host`, `share`, and optional `noperm_share`.

## Risks and Edge Cases

- The assertions intentionally encode Windows/Samba compatibility details, but several areas are filesystem-dependent. Sparse allocation granularity, hole deallocation, and copychunk sparse preservation can differ across NTFS, ReFS, XFS, Btrfs, EXT4, and Samba VFS modules.
- Some tests allow or skip behavior based on capability probes; a server that advertises a feature partially may fail deeper behavioral assertions.
- Many tests manipulate byte-range locks, async IOCTL lifetime, closed handles, bad resume keys, and undersized output buffers. These are useful regression signals but can expose server timing or implementation differences.
- `test_ioctl_qar_req()` parses repeated `file_alloced_range_buf` structures by advancing the output blob pointer, so callers must not expect the original blob pointer to remain stable after parsing.
- Cross-share copychunk tests depend on resume-key validity across tree connections in the same session and can expose differences in source-handle lifetime semantics.
- The public `test_ioctl_zero_data()` is option-driven and requires `torture:offset`, `torture:beyond_final_zero`, and `torture:filename`; unlike most suite tests it opens a caller-provided file and does not create its own.

## Test Signals

Strong pass signals include exact `NTSTATUS` matches for success and failure paths, decoded IOCTL response fields matching expected chunk/byte counts, persisted compression/sparse attributes matching expectations, file sizes unchanged by clone-like IOCTLs, deterministic data-pattern checks after copy/clone/punch operations, zero checks after hole punching, QAR range counts and offsets, and successful async IOCTL completion before close completion.

Skipped tests are expected when the target server or filesystem lacks the relevant capability. Important skip conditions include unsupported shadow copy enumeration, compression not supported or already supported for negative tests, sparse files not supported, trim not supported, block refcounting not supported, missing multichannel capability, protocol below SMB3, missing `noperm` share, and filesystem-specific sparse behavior that cannot provide the requested allocation layout.

The suite registration at the end is the operational test index. New IOCTL behavior should be added there with a stable name and should generally follow the existing pattern: capability probe first, request construction with NDR helpers, explicit status assertion, state verification, and cleanup.
