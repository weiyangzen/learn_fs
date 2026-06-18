# sources/user-network-fs/impacket/examples/ping6.py

## Purpose

`ping6.py` is a minimal IPv6 ICMP echo example. It demonstrates Impacket IPv6 and ICMPv6 packet construction, checksum calculation, raw IPv6 socket use, and ICMPv6 echo reply decoding.

## Important APIs, Types, and Functions

The script imports `IP6.IP6`, `ICMP6.ICMP6.Echo_Request`, `ImpactDecoder.ICMP6Decoder`, and `version.BANNER`. It configures IPv6 source/destination, traffic class, flow label, hop limit, next-header, payload length, and ICMPv6 checksum. It uses an `AF_INET6`, `SOCK_RAW`, `IPPROTO_ICMPV6` socket.

## Control Flow

After printing the Impacket banner and validating two positional arguments, the script creates an IPv6 packet template and a 156-byte payload. It loops forever, increments `seq_id`, creates a fresh echo request, attaches it to the IPv6 packet for metadata and checksum calculation, sends the ICMPv6 packet bytes to the destination, waits up to one second, decodes any response as ICMPv6, and prints payload size and sequence for echo replies.

## State and Persistence Behavior

State is limited to source/destination strings, the IPv6 packet object, payload bytes, raw socket, and sequence counter. There is no persistence. The only side effect is continuous ICMPv6 echo traffic until interrupted.

## Dependencies and Integration Points

It depends on raw ICMPv6 socket privileges, IPv6 routing, and Impacket ICMPv6 support. Unlike IPv4 `ping.py`, it sends `icmp.get_packet()` rather than the full IPv6 packet because the kernel handles IPv6 headers for this socket mode.

## Risks and Edge Cases

Like `ping.py`, it executes at import time and lacks argparse. It sleeps only when a packet is received, so no-reply paths loop aggressively. It does not check reply source, destination, identifier, or matching sequence beyond accepting any ICMPv6 echo reply decoded from the socket. Error messages and ICMPv6 unreachable responses are ignored.

## Test Signals

Useful tests include mocked checksum calculation and `sendto()` payloads, synthetic ICMPv6 echo reply decoding, no-argument usage behavior, raw-socket permission errors, and live loopback tests against `::1` with expected echo replies.
