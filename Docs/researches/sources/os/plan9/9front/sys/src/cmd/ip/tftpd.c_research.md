# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tftpd.c

This is a TFTP daemon implementing RFC 1350 plus option negotiation from RFC 2347/2348/2349.

Key behavior:
- Serves read and write requests over UDP using Plan 9 `announce/listen/accept`.
- Drops into user `none` and builds a namespace before serving.
- Supports `timeout`, `blksize`, and `tsize` options, including OACK responses.
- Implements retransmit/ack handling, error packets, upload creation, and download streaming.
- Supports restricted path mode, homedir selection, namespace file, net mount selection, service/address override, and filename map files.

Research notes:
- Contains PXE/u-boot compatibility handling, including Bandt MTU blksize clamping and Cavium 1432-byte exception.
- `mapname()` can substitute remote IP, PXE config MAC path, or MAC address using `/net/arp`.
