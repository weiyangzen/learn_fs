# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayoutdev.c

## Role

`filelayoutdev.c` handles GETDEVICEINFO decoding and data-server preparation for the pNFS NFSv4.1 file layout driver. It turns opaque device data into cached data-server address structures, calculates stripe/data-server indices, selects filehandles, and establishes data-server NFSv4.1 client connections.

## Deviceid allocation and decoding

`nfs4_fl_alloc_deviceid_node()` decodes the pNFS file-layout device payload from XDR pages. It reads the stripe count, validates it against `NFS4_PNFS_MAX_STRIPE_CNT`, reads `u32` stripe indices into compact `u8` storage, reads the multipath list count and validates it against `NFS4_PNFS_MAX_MULTI_CNT`, and ensures no stripe index is outside the data-server count.

It then allocates `struct nfs4_file_layout_dsaddr` with a flexible `ds_list[]`, initializes the generic deviceid node, and for each multipath list decodes addresses via `nfs4_decode_mp_ds_addr()`. Valid address lists are converted into cached `struct nfs4_pnfs_ds` objects with `nfs4_pnfs_ds_add()`. Temporary decoded address nodes are drained after each data server.

Errors free the scratch folio, stripe-index array, partially built deviceid, and temporary address list. Successful allocations retain references to each data-server object and return the filelayout device address object.

## Deviceid freeing and references

`nfs4_fl_free_deviceid()` drops each referenced data server with `nfs4_pnfs_ds_put()`, frees stripe indices, and RCU-frees the `dsaddr` through the embedded deviceid node. `nfs4_fl_put_deviceid()` drops the generic deviceid-node reference.

## Stripe and filehandle selection

`nfs4_fl_calc_j_index()` computes the stripe index from `(offset - pattern_offset) / stripe_unit`, adds `first_stripe_index`, and wraps by `stripe_count`. `nfs4_fl_calc_ds_index()` maps stripe index `j` through the decoded compact `stripe_indices` table.

`nfs4_fl_select_ds_fh()` chooses the filehandle for the selected stripe. Sparse layouts with one filehandle always use index zero; sparse layouts with zero filehandles return `NULL` so callers use the MDS OPEN filehandle; sparse layouts with multiple handles use the data-server index; dense layouts use stripe index `j` directly.

## Data-server preparation

`nfs4_fl_prepare_ds()` validates that the selected data server exists, marks the deviceid invalid if not, and connects an unconnected data server with `nfs4_pnfs_ds_connect()`. Connection failure marks the deviceid unavailable. It returns `NULL` if the data server still has no client or if the deviceid is invalid/unavailable.

Connection behavior is controlled by module parameters `dataserver_timeo` and `dataserver_retrans`, defaulting to NFSv4 data-server timeout/retransmit defaults. These parameters tune NFSv4.1 client retry behavior for data-server RPCs.

## Concurrency notes

After checking `ds->ds_clp`, the code uses `smp_rmb()` before deciding whether a connection is visible. Deviceid availability is checked after connection setup so racing invalidation or unavailable marking prevents new pNFS I/O from using the data server.
