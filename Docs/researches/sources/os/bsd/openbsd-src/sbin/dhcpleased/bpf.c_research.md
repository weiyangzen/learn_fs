# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/bpf.c

## Purpose
`bpf.c` opens and configures `/dev/bpf` for `dhcpleased` packet capture and raw DHCP packet transmission on a specific interface.

## Main Responsibilities
- Defines a read-side BPF filter accepting IPv4 UDP packets addressed to DHCP client port 68.
- Defines a write-side BPF filter allowing DHCP client-to-server packets from UDP port 68 to port 67.
- Opens `/dev/bpf` as close-on-exec and nonblocking.
- Sets the BPF buffer length to `BPFLEN`, enables immediate mode, and configures filter-drop capture behavior.
- Installs read and write filters with `BIOCSETF` and `BIOCSETWF`.
- Attaches the BPF descriptor to the named interface with `BIOCSETIF`.
- Locks the descriptor configuration with `BIOCLOCK`.

## Important APIs
- `get_bpf_sock(const char *name)`: returns a configured BPF file descriptor for `name`, or `-1` if the interface disappeared before attachment.

## Integration Notes
The main process calls this helper in response to frontend requests, then passes the resulting descriptor back to the frontend over imsg. The frontend uses it for BPF reads and broadcast DHCP writes.

## Risk Notes
Most setup failures are fatal because an incorrectly configured BPF descriptor would break DHCP operation or filtering assumptions. `BIOCSETIF` is handled non-fatally because interfaces can legitimately disappear during startup or reconfiguration.
