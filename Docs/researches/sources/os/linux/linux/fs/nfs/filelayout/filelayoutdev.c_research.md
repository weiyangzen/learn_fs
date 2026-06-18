# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayoutdev.c

## Role

`filelayoutdev.c` decodes pNFS files-layout device information, manages DS address/deviceid objects, computes stripe mappings, selects filehandles, and lazily connects to data servers.

## Deviceid Allocation And Decode

`nfs4_fl_alloc_deviceid_node()` decodes opaque GETDEVICEINFO pages with an XDR stream. It reads:
- stripe count,
- stripe index array,
- multipath list count,
- per-data-server multipath address lists.

It validates `stripe_count <= NFS4_PNFS_MAX_STRIPE_CNT`, `ds_num <= NFS4_PNFS_MAX_MULTI_CNT`, and `max_stripe_index < ds_num`. It stores stripe indices as `u8`, allocates a flexible `nfs4_file_layout_dsaddr`, initializes its generic deviceid node, decodes DS remote addresses, interns/gets `struct nfs4_pnfs_ds` objects with `nfs4_pnfs_ds_add()`, and traces decoded device info.

Failure paths free scratch folio, stripe indices, DS address lists, and partially built deviceid state.

`nfs4_fl_free_deviceid()` drops DS references, frees stripe indices, and RCU-frees the `dsaddr`. `nfs4_fl_put_deviceid()` drops the generic deviceid node reference.

## Stripe Mapping

`nfs4_fl_calc_j_index()` computes the stripe index for a file offset:
`((offset - pattern_offset) / stripe_unit + first_stripe_index) % stripe_count`.

`nfs4_fl_calc_ds_index()` maps that stripe index through the decoded `stripe_indices` array.

`nfs4_fl_select_ds_fh()` chooses the filehandle used for DS I/O. Sparse layouts use the only filehandle if `num_fh == 1`, use the MDS OPEN filehandle if `num_fh == 0`, or select by DS index. Dense layouts select by stripe index.

## Data-Server Preparation

`nfs4_fl_prepare_ds()` returns a connected `struct nfs4_pnfs_ds *` or `NULL`. It validates that a DS exists for the index, marks deviceid invalid if missing, connects to the DS through `nfs4_pnfs_ds_connect()` if needed, marks the device unavailable on connection failure, and rejects unavailable/invalid deviceids.

## Tunables

The module exposes `dataserver_retrans` and `dataserver_timeo` parameters, defaulting to NFSv4 DS retry/timeout constants, and passes them into DS connection setup.
