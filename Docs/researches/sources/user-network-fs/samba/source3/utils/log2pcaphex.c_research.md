<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/log2pcaphex.c -->
# sources/user-network-fs/samba/source3/utils/log2pcaphex.c

## Purpose
`log2pcaphex.c` extracts SMB packet traces from high-debug Samba logs and emits either raw-IP pcap data or text2pcap-compatible hex output.

## Important APIs, types, and functions
- `struct tcpdump_file_header` and `struct tcpdump_packet` describe pcap headers.
- Static IP/TCP header templates wrap SMB/NBSS payloads for raw-IP pcap output.
- `print_pcap_header()`, `print_pcap_packet()`, `print_hex_packet()`, and `print_netbios_packet()` produce the output formats.
- `read_log_msg()` reconstructs an SMB header/parameter section from `show_msg()` log output.
- `read_log_data()` reads byte dumps from `dump_data()` log output into the SMB data area.
- `main()` parses `--quiet` and `--hex`, opens optional input/output files, scans log headers, reconstructs packets, and writes output.

## Control flow
The scanner reads the input log line by line. On `show_msg` headers it starts or advances packet reconstruction and reads the structured SMB metadata lines. On `dump_data` headers during a packet, it reads the logged data bytes. When another header appears, it flushes the current packet in hex or pcap format and resets. Without `--hex`, it writes a pcap file header first.

## State and persistence behavior
Global state includes `quiet`, `hexformat`, `curpacket`, `curpacket_len`, and `line_num`. The tool writes only to the chosen output file/stdout. It allocates packet buffers dynamically and frees them after flushing.

## Dependencies and integration points
It depends on Samba SMB header offset macros from `includes.h`, popt, stdio, POSIX file APIs, endian helpers (`htons`), and the historical `show_msg()`/`dump_data()` log format. Output can be consumed by Wireshark directly as pcap or via text2pcap in hex mode.

## Risks and edge cases
- It uses `assert(fscanf(...))`, so malformed logs can abort the process.
- The NBSS length copy has a TODO about platform endian correctness.
- pcap output uses dummy IPs, ports, timestamps, and checksums.
- Samba log level 10 may truncate packets, and the tool reports incomplete traces unless quiet.
- The final packet is not flushed after EOF unless another header triggers flushing, so trailing packet handling is fragile.

## Test signals
Fixture logs containing `show_msg` and `dump_data` blocks should produce parseable pcap/hex output. Tests should cover truncated dumps, malformed lines, stdin/stdout paths, and `--quiet` warning suppression.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/log2pcaphex.c -->
