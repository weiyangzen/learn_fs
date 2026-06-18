# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ike.c

This file converts parsed `ipsecctl` IKE rules into legacy `isakmpd` FIFO configuration commands. It supports printing generated config and adding/removing IKE/IPsec connections through `/var/run/isakmpd.fifo` or a user-specified FIFO.

Key responsibilities:
- Generates `[General]`, Phase 1, identity, Phase 2, transform, and connection sections using command prefixes understood by isakmpd:
  - `C set`
  - `C add`
  - `C rms`
  - `C rmv`
- `ike_section_general` sets dynamic-mode check intervals.
- `ike_section_peer` binds peer/default Phase 1 entries, addresses, local address, and PSK auth strings.
- `ike_section_ids` emits local/remote ID sections and supplies hostname FQDN as source ID for dynamic rules without an explicit source ID.
- `ike_section_ipsec` emits Phase 2 linkage, local/remote/NAT IDs, pf tag, and sec interface.
- `ike_section_p1` maps parsed Phase 1 exchange/auth/encryption/hash/group/lifetime options to isakmpd transform settings.
- `ike_section_p2` maps Phase 2 ESP/AH encryption/auth/group/encapsulation/lifetime options to isakmpd transform settings, including AEAD/no-auth cases.
- `ike_section_p2ids` and `ike_section_p2ids_net` generate host/subnet Phase 2 ID sections and protocol/port constraints.
- `ike_connect` adds active/dynamic rules to `Connections` and passive rules to `Passive-Connections`.
- `ike_setup_ids` derives stable Phase 1/Phase 2 section names from peer/local/src/dst/proto/ports/interface/NAT information.
- `ike_gen_config` and `ike_delete_config` generate add/delete command streams.
- `ike_print_config` writes generated commands to stdout.
- `ike_ipsec_establish` opens and validates the FIFO, wraps it in `FILE *`, and writes add/delete commands.

Important dependencies:
- Consumes `struct ipsec_rule` and transform enums from `ipsecctl.h`.
- Uses address names and masks prepared by parser/address code.
- Interacts with filesystem namespace through the isakmpd FIFO path.

Security and correctness notes:
- The FIFO is validated with `fstat` and `S_ISFIFO` before use.
- Generated section names embed addresses/protocols/ports; the code assumes parser-normalized names are safe for isakmpd command syntax.
- Unsupported transforms or illegal modes produce warnings and fail generation.
