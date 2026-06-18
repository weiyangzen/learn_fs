<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_mac.c -->
# sources/test-tools/strace/src/print_mac.c

Purpose: formats MAC and hardware addresses, including device-type-specific address lengths.

Important APIs/types/functions: `print_mac_addr`, `print_hwaddr`, `sprint_mac_addr`, `sprint_hwaddr`, and `hwaddr_sizes`.

Control flow: address bytes are formatted as colon-separated hex for supported sizes, with raw quoted hex also printed in raw/verbose modes or for oversized buffers. Hardware-address printing caps displayed bytes based on ARPHRD device type where known.

State and persistence behavior: uses static formatting buffers and a static hardware-size lookup table; no dynamic state.

Dependencies and integration points: used by netlink attribute decoders and link-layer printers; depends on ARP hardware type constants, xlat verbosity, and string formatting helpers.

Risks: `hwaddr_sizes` must track ARPHRD constants. Static buffers are overwritten by later calls. Unknown device types use a permissive length cap.

Test signals: Ethernet, loopback, InfiniBand-like, unknown types, oversized address buffers, and raw/abbrev/verbose xlat modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_mac.c -->
