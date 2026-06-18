# sources/user-network-fs/impacket/examples/split.py

## Purpose

`split.py` reads an offline pcap file and splits TCP/IP traffic into one output pcap per connection. Output filenames are derived from endpoint IP addresses and ports.

## Important APIs, Types, and Functions

`Connection` stores two peer tuples, produces a filename with `getFilename()`, implements Python 2-era `__cmp__()`, and hashes both peers order-independently. `Decoder` chooses an Ethernet or Linux SLL decoder, stores a mapping of connection keys to pcap dumpers, starts pcap iteration, and handles packets in `packetHandler()`. `main()` opens the pcap with `open_offline()`, applies an `ip proto \tcp` filter, and starts decoding.

## Control Flow

The CLI prints a deprecation warning and requires one pcap filename. `main()` opens the file, filters for TCP, and calls `Decoder.start()`. Each packet is decoded to IP and TCP children, source/destination tuples are built, a connection key is checked, a new dumper is opened for first-seen connections, and the original packet is dumped to that connection's pcap.

## State and Persistence Behavior

For every observed TCP connection, the script creates a new pcap file in the current working directory. Dumpers remain open until process exit. It does not modify the input pcap.

## Dependencies and Integration Points

It depends on `pcapy.open_offline()`, `pcap.dump_open()`, BPF filtering, `EthDecoder`, `LinuxSLLDecoder`, and packet child APIs from ImpactDecoder.

## Risks and Edge Cases

The intended order-independent connection equality is not actually used because dictionary keys are string concatenations of `con.p1` and `con.p2`; reverse-direction packets can be written to a separate file. `__cmp__()` is ignored in Python 3. Filenames can collide or be unsafe in unusual address formats. Non-TCP packets are filtered, but malformed decoded packets can still break child traversal. Dumpers are not explicitly closed.

## Test Signals

Tests should cover connection filename generation, reverse-direction grouping behavior, datalink selection, dumper creation failure, malformed packet handling, and output pcap creation. Integration tests should use a small pcap with bidirectional TCP traffic to expose whether both directions land in one file.
