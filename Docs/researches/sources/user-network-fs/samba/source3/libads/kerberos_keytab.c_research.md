# sources/user-network-fs/samba/source3/libads/kerberos_keytab.c

## Purpose
`kerberos_keytab.c` synchronizes the local machine password stored in Samba secrets to Kerberos keytabs and lists keytab contents. It supports configured keytab descriptors, default keytab generation, AD-synchronized SPNs/UPN/account names, kvno and enctype synchronization, aliases, and post-sync scripts.

## Important APIs and Types
Public APIs are `sync_pw2keytabs` and `ads_keytab_list`. Core types are `enum spn_spec_type`, `struct pw2kt_specifier`, `struct pw2kt_keytab_desc`, `struct pw2kt_global_state`, and `struct pw2kt_keytab_state`. Important helpers parse configuration (`pw2kt_scan_spec`, `pw2kt_scan_line`, `pw2kt_default_cfg`), build entries from secrets (`pw2kt_process_add_pw`, `pw2kt_process_add_info`, `pw2kt_add_prefix`, `pw2kt_process_specifier`), reconcile keytabs (`pw2kt_process_keytab`, `pw2kt_process_kt2ar`), fetch AD metadata (`pw2kt_get_dc_info`), and choose defaults (`pw2kt_default_keytab_name`).

## Control Flow and Behavior
`sync_pw2keytabs` is a no-op outside domain-member role. It parses `sync machine password to keytab` or builds a default descriptor based on `kerberos method`, optionally queries AD for supported enctypes, kvno, SPNs, UPN, and sAMAccountName, initializes secrets, fetches or upgrades domain info, processes each keytab, and runs an optional sync script. `pw2kt_process_keytab` initializes Kerberos, optionally finds the strongest common AD/library enctype, expands configured specifiers into target principals, opens/creates the keytab, reads existing entries, then either replaces rolling negative-vno entries or, with real kvno sync, adds missing entries and removes stale entries by principal/vno/enctype comparison.

## State and Persistence
Persistent state includes local keytab files, Samba secrets database domain info, optional AD LDAP metadata reads, and optional side effects from `sync machine password script`. Keytab entries may include current, old, older, and next-change machine passwords with kvnos `kvno`, `kvno-1`, `kvno-2`, and `kvno+1`, or synthetic negative vnos when AD kvno sync is disabled.

## Dependencies and Integration Points
It depends on Kerberos keytab APIs, Samba Kerberos wrappers, `ads_init`/LDAP machine-account queries, secrets database upgrade/fetch, loadparm options (`sync machine password to keytab`, aliases, DNS hostnames, kerberos method), string helpers, and `smbrun`. It integrates with domain join/password rotation and service authentication that relies on local keytabs.

## Risks and Edge Cases
Configuration parsing is strict: malformed `:` or `,` separators fail the whole sync. Without `machine_password`, a descriptor is skipped. Enctype sync fails if AD and local Kerberos library share no supported enctype. Keytab reconciliation is fault-tolerant for remove failures but still returns add/open errors. Negative vno handling is unusual and warns about unexpected existing entries. Tests should cover disabled config, default config for each kerberos method, malformed specifiers, alias/additional-hostname expansion, AD metadata failures, secrets fetch failures, kvno sync vs negative-vno mode, enctype preference selection, stale entry removal, post-sync script failure, and `ads_keytab_list` output/error cleanup.
