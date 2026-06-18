# sources/user-network-fs/samba/source3/librpc/idl/secrets.idl

## Purpose
`secrets.idl` defines on-disk NDR structures for Samba source3 secrets, including trusted-domain passwords, LSA secrets, and workstation trust/domain information.

## Important APIs, types, and functions
- `TRUSTED_DOM_PASS` is a no-align, public on-disk trusted-domain password record and explicitly must not change.
- `lsa_secret` stores current/old secret blobs, timestamps, and security descriptor.
- `secrets_domain_info1_kerberos_key`, `secrets_domain_info1_password`, `secrets_domain_info1_change`, and `secrets_domain_info1` model machine account password material, Kerberos keys, domain/trust metadata, password changes, supported encryption types, salts, and rollover history.
- `secrets_domain_infoB` wraps a version enum and switch union.

## Control flow
The file has no executable logic, but its structures are consumed by secrets fetch/upgrade code. Versioned wrapper `secrets_domain_infoB` selects the v1 layout and leaves room for future glue code.

## State and persistence behavior
This is durable, security-sensitive storage. It contains cleartext blobs, NT hashes, Kerberos keys, old passwords, next-change passwords, domain SID/GUID-like DNS info via LSA structs, trust flags/types/attributes, and change timestamps. Multiple fields use `NDR_SECRET` to suppress disclosure in generated output.

## Dependencies and integration points
Imports include SAMR, LSA, Netlogon, security, and misc types. `gse_krb5.c` reads `secrets_domain_info1` to generate an acceptor keytab. Generated code is built into `NDR_SECRETS` and used by source3 secrets storage/upgrade paths.

## Risks and edge cases
The comments warn that on-disk structures must not change without version bumps and migration glue. Secret redaction, correct UTF-16 string lengths, no-align trusted-domain record layout, and preservation of old/older/next passwords are critical. Incorrect `num_keys` or key lengths can corrupt Kerberos auth.

## Test signals
Test decoding legacy trusted-domain records, LSA secret current/old pairs, domain info v1 round trips, secret redaction in dumps, password rollover with old/older/next values, and unknown version/default union handling.
