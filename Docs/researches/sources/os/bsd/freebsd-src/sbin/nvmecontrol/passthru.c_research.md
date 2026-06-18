# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/passthru.c

Purpose: Implements raw NVMe admin and I/O passthrough commands.

Key behavior:
- Registers `admin-passthru` and `io-passthru`.
- Option names and short options intentionally mirror Linux `nvme-cli` for vendor command compatibility.
- Accepts opcode, command dwords, namespace ID, timeout, flags, data length, input file, raw-binary output, dry-run, read/write direction, and prefill byte.
- Allocates page-aligned payload memory for data transfers.
- For write commands, reads exactly `data_len` bytes from input file or stdin.
- Builds `struct nvme_pt_command` and submits it through `NVME_PASSTHROUGH_CMD`.
- Prints completion DWORD0 and hex dumps read data unless raw binary output is requested.

Dependencies:
- `nvmecontrol.h` for command registration, `open_dev()`, and `print_hex()`.
- FreeBSD NVMe passthrough ioctl.

Research notes:
- Metadata transfer is explicitly unsupported on FreeBSD in this path.
- The FreeBSD kernel overrides NSID, noted by an inline `XXX`.
