# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/cec.c

This file implements `cec`, the Coraid Ethernet console client.

Key behavior:
- Parses options for service posting, escape character, debug, target Ethernet address, host, persistent probing, shelf, and interface.
- Discovers shelves by broadcasting `Tdiscover` packets and collecting `Toffer` replies.
- Filters discovered shelves by shelf number, host name, or Ethernet address, then sorts and optionally prompts for selection.
- Establishes a console connection with a three-step Ethernet handshake (`Tinita`, `Tinitb`, `Tinitc`).
- Runs an interactive loop multiplexing keyboard input and Ethernet console packets.
- Sends data packets with sequence numbers, handles ACK/reset, retransmits outstanding keyboard data on timeout, and writes received data to stdout after CR stripping.
- Supports escape commands to quit, interrupt, or continue.
- Can post itself under `/srv` and connect stdin/stdout to a pipe for service use.

Important details:
- Uses private EtherType `0xbcbc`.
- Console raw mode is skipped when running as a posted service.
- `exits0()` cleans up raw mode, active connection, and `/srv` file.
- Packet headers use local helper byte-order conversions.

Filesystem relevance:
- Indirect. Uses `/srv`, `/net/ether*/...`, and console control files, but is not a filesystem implementation.
