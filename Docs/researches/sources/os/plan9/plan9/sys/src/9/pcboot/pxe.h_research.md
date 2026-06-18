# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/pxe.h

This header defines the minimal BOOTP/TFTP/UDP protocol structures and constants used by the PXE boot loader.

Key contents:
- Ethernet/IP/UDP protocol constants, BOOTP ports, TFTP opcodes, default timeout, and default TFTP segment size.
- BOOTP option constants including end, padding, and subnet mask.
- `Udphdr`, Plan 9’s UDP pseudo-header/control-message layout.
- `Bootp`, matching the BOOTP packet layout with DHCP-style option area.
- `Pxenetaddr`, a compact IP-plus-port tuple used by PXE code.
- External `chatty` declaration.

Filesystem/storage relevance:
- Supports network boot image retrieval rather than local filesystems.
- Provides protocol layout consumed by `pxeload.c`.
