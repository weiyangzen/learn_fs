# sources/user-network-fs/nfs-ganesha/src/include/fsal_pnfs.h

Purpose: This header defines FSAL-level pNFS structures for metadata server layout handling, device IDs, data server handles, and layout return/commit bookkeeping.

Important APIs/types/functions: `struct pnfs_segment` models layout IO mode, offset, and length. `enum fsal_id` assigns FSAL IDs embedded in pNFS `deviceid4`. `struct pnfs_deviceid` is the host-order FSAL view of a deviceid. `struct fsal_layoutget_arg`/`res`, `struct fsal_layoutreturn_arg`, `struct fsal_layoutcommit_arg`/`res`, and `struct fsal_getdevicelist_res` are the argument contracts consumed by `fsal_api.h` layout vectors.

Control flow: An MDS advertises support, answers `GETDEVICEINFO`/`GETDEVICELIST`, grants layouts via `layoutget`, receives returns through `layoutreturn`, and accepts client write aggregation through `layoutcommit`. FSAL-provided segment data is saved by the state layer and passed back on return/commit.

State and persistence: Layout state includes segment ranges, per-segment FSAL data, layoutget context, return-on-close flags, recall cookies, cookie verifiers, and client-visible device IDs. The header warns that allocated segment/context data must be freed at disposal or completion boundaries.

Dependencies and integration points: Includes `nfs4.h` and feeds the FSAL object/export operation vectors, NFSv4.1 layout operations, pNFS DS read/write/commit paths, and upcall layout recall.

Risks: Device IDs are host-order opaque data, so cross-platform assumptions are risky. Forgetting to set `last_segment` or free `fsal_seg_data`/contexts leaks or loops. Multiple-segment support is possible but production clients often expect a single segment.

Test signals: Test layout type advertisement, layoutget single and multi-segment paths, getdevicelist cookies/verifiers, layoutreturn circumstances including revoke/reclaim/shutdown, layoutcommit size/time changes, and recall-cookie satisfaction.
