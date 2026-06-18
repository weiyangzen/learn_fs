# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tnet.h

## Purpose
Trusted Extensions labeled networking function declarations.

## Main Interfaces
- Defines `TSOL_MAX_IPV6_OPTION`.
- Declares host/template lookup and checking routines such as `tsol_tnrh_chk` and `find_rhc`.
- Declares IPv4/IPv6 security option manipulation routines: `tsol_prepend_option`, `tsol_prepend_option_v6`, `tsol_remove_secopt`, and `tsol_remove_secopt_v6`.
- Declares gateway security attribute allocation/free and initialization helpers.
- Declares packet label and receive-attribute routines such as `tsol_get_pkt_label`, `tsol_attr_to_zoneid`, `tsol_get_option_v4`, and `tsol_get_option_v6`.
- Declares routing/forwarding helpers including `tsol_ire_match_gwattr`, `tsol_rtsa_init`, `tsol_ire_init_gwattr`, `tsol_ip_forward`, and `tsol_pmtu_adjust`.

## Dependencies And Relationships
Includes STREAMS, TSOL label/database headers, IPv4/IPv6, IP, and routing headers. It is consumed by IP stack code enforcing labeled networking rules.

## Research Notes
The header separates database/cache definitions in `tndb.h` from packet-path operations that add, strip, inspect, and route security label options.
