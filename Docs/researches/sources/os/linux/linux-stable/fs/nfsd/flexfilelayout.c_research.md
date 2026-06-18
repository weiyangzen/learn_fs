# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayout.c

## Summary
Implements a minimal NFSv4.1 pNFS flex-file layout server where the metadata server is also the data server.

## Main APIs
Exports `ff_layout_ops` with layoutget, getdeviceinfo, layoutcommit, and XDR encoder hooks.

## Behavior
`nfsd4_ff_proc_layoutget()` allocates one flex-file layout containing one mirror, one data server, and one filehandle. It sets flags to avoid layoutcommit, force I/O away from MDS, and disable read I/O for RW layouts. It copies the current filehandle into the layout and grants a whole-file segment. `nfsd4_ff_proc_getdeviceinfo()` builds a TCP or TCP6 netaddr from the request destination address and advertises payload-sized read/write sizes. Layoutcommit is a no-op.

## Risks
This is intentionally simple and tightly coupled to the server address observed on the request. The UID adjustment for read layouts is a permission trick and depends on client/server interpretation of flex-file credentials.
