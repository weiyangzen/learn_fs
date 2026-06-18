# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/ipsecctl.c

This is the main `ipsecctl` command front-end. It parses command-line options, loads rules, commits them to PF_KEY or isakmpd, flushes state, shows SPD/SAD state, monitors PF_KEY, prints rules, and manages parsed rule memory.

Key responsibilities:
- `main` handles options:
  - `-c` collapse rules
  - `-D macro=value`
  - `-d` delete
  - `-f file` load rules
  - `-F` flush
  - `-i fifo` select isakmpd FIFO
  - `-k` show keys
  - `-m` monitor
  - `-n` dry run
  - `-v` verbose / extra verbose
  - `-s flow|sa|all` show state
- `ipsecctl_rules` initializes parse state, invokes `parse_rules`, commits add/delete actions unless dry-run, and frees all parsed rules.
- `ipsecctl_fopen` opens config files and rejects directories.
- `ipsecctl_commit` opens PF_KEY and dispatches each rule to either `ike_ipsec_establish` for IKE rules or `pfkey_ipsec_establish` for static PF_KEY rules.
- `ipsecctl_add_rule` queues rules and optionally prints them in verbose dry-run style.
- `ipsecctl_free_rule` frees nested address, auth, transform, lifetime, key, and generated-name allocations.
- `ipsecctl_merge_rules`, `ipsecctl_cmp_ident`, `ipsecctl_rule_matchsrc`, and `ipsecctl_rule_matchdst` implement collapsed display grouping for compatible flow rules.
- Print helpers render addresses, protocols, ports, keys, flows, SAs, bundles, and whole rules.
- `ipsecctl_flush` flushes PF_KEY-managed IPsec state unless dry-run.
- `ipsecctl_get_rules` and `ipsecctl_parse_rules` dump and parse SPD rules from `sysctl` `NET_KEY_SPD_DUMP`.
- `ipsecctl_show` dumps flows and/or SAs, pledges down after data collection, sorts SAD entries by SPI, and prints state.
- `ipsecctl_monitor` delegates to PF_KEY monitor code.
- `unmask` computes prefix length from stored masks.

Important OS interactions:
- Uses PF_KEY sysctl dumps:
  - `NET_KEY_SPD_DUMP`
  - `NET_KEY_SADB_DUMP`
- Uses PF_KEY backend functions from files outside this work item.
- Uses `pledge("stdio dns")` and then `pledge("stdio")` in show mode.
- Opens config/FIFO paths through standard file APIs.

Security and correctness notes:
- Dry-run mode avoids committing or flushing.
- `-k` can print key material, so output must be treated as sensitive.
- Rule collapse assumes sorted SPD dump order; the code explicitly notes that only comparing with the last entry depends on sorted input.
