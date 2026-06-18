# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/mds.c

## Purpose

`mds.c` implements Ceph FSAL pNFS metadata-server support under `CEPH_PNFS`: device info/list reporting, layout capability queries, layout grants, layout returns, and layout commits. The complete 698-line file was read for this report.

## Important APIs, Types, and Functions

Key functions are `initiate_recall`, `getdeviceinfo`, `getdevicelist`, `fs_layouttypes`, `fs_layout_blocksize`, `fs_maximum_segments`, `fs_loc_body_size`, `fs_da_addr_size`, `export_ops_pnfs`, `layoutget`, `layoutreturn`, `layoutcommit`, and `handle_ops_pnfs`. Important structures include `struct ceph_file_layout`, `struct pnfs_deviceid`, `struct ds_wire`, `struct pnfs_segment`, `struct fsal_layoutget_arg/res`, and `struct fsal_layoutcommit_arg/res`.

## Control Flow

`export_ops_pnfs` registers export pNFS methods. `getdeviceinfo` validates files layout type, derives the file layout from an inode encoded in the device id, emits a fixed 1024-stripe index array, then encodes one NFS multipath address per Ceph OSD. `layoutget` validates the requested layout type, fetches Ceph file layout, constrains or expands the segment for Linux client behavior, tracks issued read/write layout counters under object lock, builds a DS wire handle carrying the filehandle and Ceph layout, then XDR-encodes a file layout. `layoutreturn` decrements issued counters when disposing layouts. `layoutcommit` fetches old size/mtime, grows size if needed, selects a commit mtime, and writes attributes back.

## State and Persistence Behavior

The file tracks pNFS layout counters (`rd_issued`, `rw_issued`, serials, max length) in `struct ceph_handle` when pNFS is compiled. Device info is generated from live Ceph OSD and file-layout state rather than stored locally. Layout commit can persist size and mtime changes to CephFS. Layout return is mostly bookkeeping because the actual Ceph cap hold/return calls are disabled in `#if 0` blocks.

## Dependencies and Integration Points

Dependencies include libcephfs pNFS/layout helpers, Ganesha pNFS XDR helpers, IP utility multipath encoding, upcall layout recall vectors, and Ceph handle/export state from `internal.h`. It integrates with `export_ops_init` and `handle_ops_init` only when `CEPH_PNFS` is defined.

## Risks and Edge Cases

This file shows concrete bit-rot risk in the inspected tree: several references (`handle->vi`, `handle->wire`, pointer-style `stxnew->...`, direct `op_ctx->creds` argument where wrappers expect a pointer) do not match the current `internal.h`/compat wrapper shapes. These may be hidden by `CEPH_PNFS` being disabled, but should be treated as compile blockers when enabling pNFS. Layout range handling intentionally lies for whole-file Linux client requests. OSD address encoding assumes NFS port 2049 and one host per OSD. Counter decrement in write-layout paths appears to decrement `rd_issued` in places where `rw_issued` is expected.

## Test Signals

Minimum signals are a `CEPH_PNFS` build, layoutget/layoutreturn/layoutcommit integration tests, device info XDR decode tests with varied OSD counts and stripe units, bad layout type and out-of-range layout requests, whole-file Linux layout requests, layout counter balance under failures, DS wire-handle decode by the data-server side, and layoutcommit size/mtime monotonicity.
