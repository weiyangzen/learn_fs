# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/pflogd.c

## Purpose

Main implementation of `pflogd`, the PF log daemon. It captures packets from a `pflog(4)` interface through BPF/libpcap and appends them to a pcap-format log file, using privilege separation for BPF and log-file access.

## Main State

Global capture state includes `hpcap`, output `FILE *dpcap`, configured and current snaplen, signal flags, log filename, interface name, optional pcap filter, flush delay, output buffer state, suspend state, and dropped-packet count. Default configuration is `pflog0`, `/var/log/pflog`, snaplen `DEF_SNAPLEN`, read timeout `PCAP_TO_MS`, and flush delay `FLUSH_DELAY`.

## Capture Setup

`pflog_read_live()` creates a pcap handle but manually opens `/dev/bpf` read-only, verifies BPF version, attaches the requested interface with `BIOCSETIF`, sets datalink type `DLT_PFLOG`, installs timeout and optional promiscuous mode, queries BPF buffer length with `BIOCGBLEN`, allocates the pcap buffer, and marks the handle activated. `init_pcap()` checks the datalink type, installs the compiled filter via `set_pcap_filter()`, and locks the BPF descriptor with `BIOCLOCK`.

## Log File Handling

`reset_dump()` closes any previous pcap output after flushing the local buffer, asks the privileged process to open the log, wraps the fd with `fdopen("a+")`, disables stdio buffering, and either writes a new pcap file header or validates an existing file with `scan_dump()`. Existing logs are scanned end-to-end for header compatibility, packet header integrity, captured length bounds, and exact file-size match before append. If an existing log has a different snaplen, the daemon attempts to switch to that snaplen.

## Packet Writing

`dump_packet()` appends packet headers and payloads into a private `PFLOGD_BUFSIZE` buffer, flushing when needed. Oversized packets or packets larger than current snaplen are dropped. If a packet cannot fit even after flushing, `dump_packet_nobuf()` writes it directly. `flush_buffer()` records the current file offset, writes the buffer, truncates back to the saved offset on failure, suspends logging on errors, and resets buffer cursors on success. `purge_buffer()` drops buffered packets and accounts them as dropped.

## Main Loop

`main()` parses `-D`, `-d`, `-f`, `-i`, internal `-P`, `-s`, and `-x`; validates the interface; optionally daemonizes; builds the optional filter expression; starts privilege separation with `priv_init()`; pledges to `stdio recvfd`; installs signal handlers; initializes pcap through the privileged parent; allocates the output buffer; opens/validates the log; then loops on `pcap_dispatch()`.

Signals are converted into flags after `pcap_breakloop()`: close exits, HUP reopens the log and resumes if possible, and ALRM flushes periodically or triggers reopen if no output file exists. `-x` exits after validating/opening the log path.

## Risks And Invariants

- `scan_dump()` may take a long time on large log files because it validates every packet before append.
- Logging suspension is deliberate: write/open failures stop further log writes but the daemon keeps consuming packets and counting drops.
- Snaplen changes purge buffered packets when shrinking to avoid writing packets incompatible with the new capture length.
- The code reaches into `pcap_t` internals (`pcap-int.h`), so it is coupled to OpenBSD's libpcap layout.
- Direct BPF setup and log opening are intentionally routed through privilege separation; bypassing that would break the daemon's security model.
