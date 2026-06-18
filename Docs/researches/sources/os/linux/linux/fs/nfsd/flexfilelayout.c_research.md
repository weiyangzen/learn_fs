# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayout.c

Read completely: 144 lines.

Minimal pNFS flex-file layout server implementation where the metadata server is also the data server and both serve the same underlying storage.

Key responsibilities:
- Implements layoutget by allocating one `pnfs_ff_layout`, setting flags that avoid layoutcommit, avoid I/O through the MDS, and disable read I/O for RW layouts.
- Adjusts the UID for read-only layouts so an IOMODE_READ segment does not carry write permissions.
- Sets a deviceid from the filehandle, copies the NFS filehandle into the layout, and returns a whole-file layout segment.
- Implements getdeviceinfo by building one data-server address from the request destination address and port, using `tcp` or `tcp6`, and setting NFSv3 data-server version and payload sizes.
- Implements layoutcommit as a no-op success.
- Publishes `ff_layout_ops` with device notification support, disabled recalls, and flexfile XDR encoders.

Dependencies:
- Uses pNFS layout structures, `svc_max_payload`, `rpc_ntop`, request destination socket address, and flexfile XDR definitions.

Notable risks:
- This is intentionally simple and assumes a single mirror, data server, filehandle, and whole-file segment.
- Device address formatting must fit fixed buffers sized in `flexfilelayoutxdr.h`.
