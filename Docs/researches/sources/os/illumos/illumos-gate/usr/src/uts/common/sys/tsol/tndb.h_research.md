# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tsol/tndb.h

## Purpose
Trusted network database definitions for remote host templates, CIPSO options, multilevel ports, caches, and labeled network lookup helpers.

## Main Interfaces
- Defines `tnaddr_t` for IPv4/IPv6 addresses and helpers for comparing addresses.
- Defines database operation enum `tsol_dbops_t`.
- Defines remote host entries/string forms `tsol_rhent_t` and `tsol_rhstr_t`.
- Defines CIPSO constants, tag type 1 structure, and `cipso_option_t`.
- Defines well-known Trusted Solaris classifications and compartment authority bits.
- Defines template strings such as `TP_UNLABELED`, `TP_CIPSO`, `TP_ZONE`, `TP_HOSTTYPE`, `TP_DOI`, `TP_DEFLABEL`, `TP_MINLABEL`, `TP_MAXLABEL`, and `TP_SET`.
- Defines template structures for unlabeled and CIPSO hosts, collected in `tsol_tpent_t` and `tsol_tpstr_t`.
- Defines multilevel port entry `tsol_mlpent_t` and zone cache entry `tsol_zcent_t`.
- Defines cached template and remote-host cache objects `tsol_tpc_t` and `tsol_tnrhc_t`, with hold/release macros.
- Defines cache sizing and hashing macros for IPv4/IPv6 address and mask lookup.
- Declares `tnrhc_free`, `tpc_free`, `find_tpc`, `tcache_init`, `tsol_next_port`, `tsol_mlp_port_type`, `tsol_mlp_findzone`, `tsol_mlp_anon`, `tsol_print_label`, `rtsa_validate`, `gcgrp_lookup`, `gcgrp_inactive`, and `tnrh_load`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/zone.h`, TSOL label headers, and networking headers. Used by Trusted Extensions network policy, routing security attributes, and multilevel port enforcement.

## Research Notes
This is the central TSOL labeled-network data model. It combines persistent database concepts with in-kernel reference-counted caches, so lifetime macros are as important as structure layout.
