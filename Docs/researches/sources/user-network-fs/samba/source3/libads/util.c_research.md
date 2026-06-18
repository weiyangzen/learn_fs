# sources/user-network-fs/samba/source3/libads/util.c

## Purpose

`util.c` contains two ADS utility areas: Kerberos-based machine trust password change for domain members, and parsing of Windows-style SPN strings.

## Important APIs, Types, and Functions

Under `HAVE_KRB5`, `ads_change_trust_account_password` rotates the machine account password via Kerberos set-password. `parse_spn` parses `service/host[:port][/servicename]` into `struct spn_struct` fields: service class, host, optional port, and optional service name.

## Control Flow

The password-change path verifies the server role is `ROLE_DOMAIN_MEMBER`, generates a workstation trust password, stages the change in secrets with keytab sync support, rejects recovery if a previous change already exists, converts current and next stored UTF-16MUNGED passwords to Unix strings, calls `kerberos_set_password`, records failure with `secrets_failed_password_change` on conversion or remote errors, and finalizes with `secrets_finish_password_change` on success.

`parse_spn` allocates a result, duplicates the input as mutable serviceclass storage, splits at the first slash, then optional colon and second slash. It rejects missing or empty host, empty service name, empty port, out-of-range ports, and conversion range errors. Pointers for host and service name point inside the duplicated serviceclass buffer.

## State and Persistence Behavior

Password change persists staged and completed machine password state in Samba secrets and can update keytabs. SPN parsing has no persistent state; parsed fields are talloc-owned by the caller.

## Dependencies and Integration Points

The password path depends on Kerberos set-password, secrets password-change helpers, ADS/KDC connection state, loadparm role/workgroup, trust password generation from `trusts_util.c`, and optional keytab sync. `parse_spn` is used by `net_ads_setspn.c` and any command path validating SPN syntax.

## Risks and Test Signals

Risks include partial secrets state after Kerberos failures, role restrictions, previous-change recovery being rejected rather than repaired here, secret cleartext conversion failures, `parse_spn` storing subfield pointers inside a single mutable buffer, and `errno` handling around `strtol`. Tests should cover domain-member role enforcement, successful and failed Kerberos set-password, secrets prepare/finish/fail paths, SPNs with port and service name, malformed missing-host/no-slash/empty-port/empty-service cases, port bounds, and lifetime of parsed subfields.
