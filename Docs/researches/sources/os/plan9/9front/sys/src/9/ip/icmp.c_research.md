# File Research: sources/os/plan9/9front/sys/src/9/ip/icmp.c

Implements ICMPv4 as protocol number 1. It supports user ICMP conversations, echo reply handling, generated error messages, protocol advice delivery, source-translation forwarding, and statistics.

Key responsibilities:
- Registers protocol `icmp`.
- Sends user-provided ICMP packets through `icmpkick()`.
- Receives ICMP packets through `icmpiput()`.
- Responds to echo requests with echo replies.
- Generates errors through `icmpnohost()`, `icmpnoconv()`, `icmpcantfrag()`, and `icmpttlexceeded()`.
- Converts unreachable/time-exceeded messages into protocol advice.
- Supports ICMP forwarding/NAT translation via `icmpforward()` and `icmpproxyadvice()`.

Important implementation details:
- `Icmppriv` stores MIB-like counters and per-type in/out counts plus an `Ipht` hash table for translations.
- Generated ICMP errors include the original packet up to IPv4 minimum MTU.
- ICMP errors are not sent for multicast addresses or when no valid local source can be selected.
- `goticmpkt()` demultiplexes by ICMP id and can reverse NAT translations.
- Advice only proceeds when the embedded IPv4 packet has no options, is first fragment, and has a valid checksum.
- `hnputs_csum()` is used to adjust checksums during translation.

Dependencies and integration:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsconnected`, and `Fsrcvpcolx`.
- Sends packets through `ipoput4()`.
- Provides hooks used by IP fragmentation and ARP timeout paths.

Research notes:
- ICMPv4 is both a user-visible datagram protocol and an internal control/error mechanism.
- NAT behavior is integrated into the protocol using `Proto.ht` and translation helpers from `ipaux.c`.
