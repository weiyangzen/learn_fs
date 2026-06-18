# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.c

This file implements KeyNote policy integration and KeyNote credential handling for isakmpd.

Global policy state:
- `policy_asserts`, `policy_asserts_num`: loaded KeyNote policy assertions.
- `ignore_policy`: bypass switch.
- `policy_exchange`, `policy_sa`, `policy_isakmp_sa`: current exchange/SA context used by `policy_callback()`.

Main policy callback:
- `policy_callback(char *name)` is the central KeyNote callback provider.
- On `KEYNOTE_CALLBACK_INITIALIZE` or cleanup, it resets cached static strings and allocated filters/IDs.
- On first real lookup after reset, it populates a large cached environment from negotiated phase 2 protocols, chosen transforms, phase 1 SA identity, phase 2 local/remote IDs, transport addresses, PFS, encapsulation, lifetimes, algorithms, ports, protocol numbers, and initiator role.
- Returns KeyNote attribute strings for names such as `esp_present`, `ah_present`, `remote_filter`, `local_filter`, `remote_id`, `phase_1`, `GMTTimeOfDay`, `LocalTimeOfDay`, `pfs`, `initiator`, `phase1_group_desc`, algorithm names, lifetimes, ECN flags, and negotiation addresses.

Policy initialization:
- `policy_init()` checks `General/Use-Keynote`, opens the configured policy file through `monitor_open`, verifies file secrecy, reads the whole file, parses assertions with `kn_read_asserts`, and replaces the global assertion array.

Credential helpers:
- `keynote_cert_init()`: no-op success.
- `keynote_cert_get()`: copies raw credential bytes to a NUL-terminated string.
- `keynote_cert_validate()`: parses assertions and verifies signatures.
- `keynote_cert_insert()`: adds parsed credential assertions to a KeyNote session.
- `keynote_cert_free()`: frees credential memory.
- `keynote_certreq_validate()`: validates a KeyNote public key request by decoding it.
- `keynote_certreq_decode()` and `keynote_free_aca()`: stubs.
- `keynote_cert_obtain()`: locates credential files under `KeyNote/Credential-directory` by IPv4/IPv6 address or FQDN/user FQDN ID and reads them.
- `keynote_cert_get_key()`: extracts an RSA/X509 licensee public key from credentials.
- `keynote_cert_dup()`, `keynote_serialize()`, `keynote_printable()`, `keynote_from_printable()`: string duplication/serialization wrappers.
- `keynote_ca_count()`: returns 0 because trusted CAs are treated elsewhere.

Dependencies:
- KeyNote library: `kn_read_asserts`, `kn_verify_assertion`, `kn_add_assertion`, `kn_get_licensees`, `kn_decode_key`.
- OpenSSL RSA duplication for credential key extraction.
- isakmpd subsystems: configuration, exchange, IPsec DOI structures, transport address decoding, monitor file access, secrecy checks, X.509 DN formatting.

Risk notes:
- `policy_callback()` relies on global current-context pointers and static cached buffers, making it single-context and not reentrant.
- The callback contains repeated ID formatting logic for IPv4/IPv6 address, range, subnet, FQDN, user FQDN, ASN.1 DN, and key ID forms; consistency bugs are easy here.
- Several Key ID hex conversion loops use the first byte expression repeatedly rather than indexing by loop counter, which is suspicious for non-printable Key IDs.
- `keynote_cert_insert()` adds assertions but does not free the parsed assertion strings after insertion in the visible code path.
