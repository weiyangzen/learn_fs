# File Research: sources/os/plan9/9front/sys/src/9/ip/pktmedium.c

Implements the packet pseudo-medium for user-visible IP packet queues.

Key elements:
- Defines a `pkt` medium with 4 KiB MTU and automatic unbind-on-close.
- Bind/unbind are no-ops.
- Writes outbound packets into the interface conversation read queue.
- Copies packets to the snoop queue when snoopers are present.

Dependencies:
- Used by `ipifcconnect` as the default medium when a dial-style interface has not been explicitly bound.

Research notes:
- This medium turns an `ipifc` conversation into a packet endpoint rather than a hardware-backed interface.
