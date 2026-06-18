# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkdump.c

This file decodes and prints PF_KEY SADB messages for `ipsecctl`.

Key responsibilities:
- Maps PF_KEY message, extension, SA, algorithm, state, identity, flow, and flag numeric IDs to human-readable names.
- Prints SADB extensions in verbose monitor/dump output.
- Reconstructs `struct ipsec_rule` views from SADB SA messages for normal `ipsecctl` rule-style output.
- Supports monitor output for live PF_KEY messages.
- Prints raw PF_KEY byte dumps when requested.

Important functions and data:
- `ext_types`, `msg_types`, `sa_types`, `auth_types`, `enc_types`, `comp_types`, `flag_types`, `identity_types`, `flow_types`, and `states` are local lookup tables.
- `setup_extensions()` walks a PF_KEY message and indexes extensions by extension type.
- `pfkey_print_sa()` converts SADB SA messages back into `struct ipsec_rule` and calls `ipsecctl_print_rule`.
- `pfkey_monitor_sa()` prints message header and each extension.
- `pfkey_print_raw()` prints raw bytes.
- `pfkey_get_spi()` extracts the SPI from an indexed SA extension.
- `print_sa()`, `print_addr()`, `print_key()`, `print_life()`, `print_flow()`, `print_counter()`, and related helpers format individual extension types.
- `parse_addr()`, `parse_key()`, and `parse_satype()` adapt SADB extensions into `ipsecctl` structures.

Notable behavior:
- Authentication and encryption algorithm variants are inferred from PF_KEY algorithm IDs and key lengths.
- Key material is hidden unless `IPSECCTL_OPT_SHOWKEY` is set; key extensions are nulled before rule printing when hidden.
- `print_key()` zeroes key bytes after printing them.
- Bundle output is reconstructed when `SADB_X_EXT_SA2`, `SADB_X_EXT_DST2`, and `SADB_X_EXT_SATYPE2` are present.
- Verbose output prints all known extensions after the reconstructed rule.

Dependencies:
- Uses `ipsecctl.h` structures and transform arrays declared elsewhere.
- Uses `pfkey.h` for public PF_KEY dump/monitor prototypes.
- Consumes OpenBSD PF_KEY V2 and IPsec extension definitions from system headers.

Research notes:
- This module is read-only/diagnostic relative to the kernel, but it must mirror encoding decisions in `pfkey.c` and transform tables in `parse.y`.
