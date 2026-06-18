# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_tftproot.c

Read completely: 459 lines.

This file downloads a root RAM disk over TFTP during root mount setup. It uses the NFS diskless boot machinery to discover the server/interface and then uses a UDP socket to fetch the boot file block by block.

Main flow:
- `tftproot_dhcpboot` selects the boot interface from `rootspec` or `bootdv`, sets `root_device`, allocates an `nfs_diskless`, calls `nfs_boot_init`, strips a leading `tftp:` prefix from `nd_bootfile`, and invokes `tftproot_getfile`.
- `tftproot_getfile` opens a UDP socket, applies the NFS boot receive timeout, builds a TFTP RRQ packet in octet mode, repeatedly calls `nfs_boot_sendrecv`, turns the outgoing packet into ACKs, and finally passes the downloaded buffer to `md_root_setconf`.
- `tftproot_recv` validates incoming TFTP packets, handles DATA and ERROR opcodes, checks block sequencing, detects final short block, grows the receive buffer with `realloc`, and appends payload data.

Integration: this ties together network boot (`nfs_boot_init`, `nfs_boot_sendrecv`), interface lookup, mbufs/sockets, and memory disk root setup. It uses TFTP constants copied from the standalone boot code.

Reliability/security notes: the protocol path is deliberately simple and unauthenticated, as TFTP is. Packets are length-checked against the 512-byte TFTP segment size and block number is enforced. The accumulated RAM disk is grown to the full file size in kernel memory, so boot environment control and file size matter for memory pressure.
