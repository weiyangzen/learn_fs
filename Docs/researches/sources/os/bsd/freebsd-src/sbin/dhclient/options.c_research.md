# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/options.c

## Purpose
Parses DHCP option buffers from received packets, expands RFC 3397 domain-search options, builds outbound option buffers, formats option values for lease files/script environments, and dispatches fully parsed packets.

## Main Elements
- Receive parsing:
  - `parse_options()` validates the DHCP cookie, parses main options, handles option overload in `file`/`sname`, and expands domain search.
  - `parse_option_buffer()` walks TLV options, concatenates repeated options, rejects malformed lengths, and has a limited tolerance path for repeated bogus offers.
- Domain search:
  - `expand_domain_search()` converts DNS-label encoded option 119 into a space-separated textual list.
  - `find_search_domain_name_len()` validates labels, compression pointers, truncation, and forward-pointer loops.
  - `expand_search_domain_name()` copies already-validated compressed names.
- Outbound options:
  - `cons_options()` builds option data according to maximum message size, priority list, overload policy, and termination rules.
  - `store_options()` emits prioritized options, splits values over 255-byte chunks and overload boundaries, and skips options that do not fit.
- Formatting and dispatch:
  - `pretty_print_option()` formats options according to `dhcp_options[code].format`.
  - `do_packet()` wraps raw packets in `struct packet`, parses options, identifies DHCP message type, calls `dhcp()` or `bootp()`, and frees parsed option storage.

## Dependencies And Integration
Uses `dhcp_options[]`, `dhcp_option_default_priority_list`, conversion helpers, inet formatting, and `dhclient.c` packet handlers. Tests in `option-domain-search.c` target the domain-search expansion logic.

## Risk Notes
Network-provided option lengths, repeated options, compression pointers, and text formatting are attack surface. The domain-search parser rejects truncated and forward/self-referential pointers before copying. `pretty_print_option()` uses a large static buffer and warns on overflow.
