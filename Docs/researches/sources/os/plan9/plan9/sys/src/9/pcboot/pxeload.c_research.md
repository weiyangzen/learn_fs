# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/pxeload.c

This file implements the Plan 9 PXE network boot path using BOOTP and TFTP on top of the kernel’s Ethernet/IP device interfaces.

Key responsibilities:
- Discovers Ethernet interfaces, binds their `#I` and `#l` device trees into `/net`, and creates temporary IP/UDP configuration.
- Sends BOOTP broadcasts, validates replies by hardware address and optional server name, and extracts client/server addressing.
- Opens TFTP sessions using either UDP pseudo-headers or connected UDP channels.
- Negotiates TFTP block size via `blksize`, tracks block numbers, ACKs data, handles OACK/error packets, and streams kernel bytes into `bootpass`.
- Reads optional `/cfg/pxe/<etheraddr>` via TFTP, runs `dotini`, and uses `bootfile` or interactive prompts to choose a kernel.
- Retries across Ethernet interfaces and keeps retrying after failures.

Important functions:
- `etheraddr`, `binddevip`, `openetherdev`, `minip4cfg`, `ip4cfg`, and `unminip4cfg` handle temporary network setup.
- `bootpbcast` performs BOOTP discovery.
- `tftpopen`, `tftpread1st`, `tftpread`, `tftprdfile`, and `tftpboot` implement TFTP loading.
- `rdcfgpxe`, `getkernname`, and `parsebootfile` choose the next kernel and preserve arguments in `BOOTLINE`.
- `bootloadproc` is the long-running boot process.

Filesystem/storage relevance:
- Provides a network-backed alternative to disk boot by loading kernels and configuration over TFTP.
- Uses Plan 9 channels and device operations rather than a standalone network stack.
