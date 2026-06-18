# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.h

This header exports KeyNote policy and credential support.

Key definitions:
- Credential file names: `CREDENTIAL_FILE` and `PRIVATE_KEY_FILE`.
- Global policy variables: `ignore_policy`, `policy_asserts_num`, `policy_asserts`, `policy_exchange`, `policy_sa`, `policy_isakmp_sa`.

Exported APIs:
- Policy lifecycle and callback: `policy_init()`, `policy_callback()`.
- KeyNote credential hooks: init, get, validate, insert, free, certreq validate/decode, ACA free, cert obtain, subject extraction, key extraction, duplication, serialization, printable conversion, and CA count.

Integration:
- Used by authentication, certificate, and policy-decision code to bridge isakmpd’s internal SA/exchange state into KeyNote.
