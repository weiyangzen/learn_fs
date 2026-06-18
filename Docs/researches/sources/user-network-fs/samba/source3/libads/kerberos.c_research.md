# sources/user-network-fs/samba/source3/libads/kerberos.c

## Purpose
`kerberos.c` implements source3 Kerberos utility operations: password-based kinit, multi-secret kinit using passwords or NT hashes, explicit-KDC AS exchange over TCP, credential-cache destruction, key derivation from strings, KDC discovery formatting, and local private `krb5.conf` generation for AD domains.

## Important APIs and Functions
Public APIs are `kerberos_kinit_password_ext`, `kerberos_kinit_passwords_ext`, `ads_kdestroy`, `create_kerberos_key_from_string`, `kerberos_kinit_password`, and `create_local_private_krb5_conf_for_domain_internal`. Internal building blocks include `kerb_prompter`, `kerberos_kinit_generic_once`, password callback `kerberos_kinit_password_ext_cb`, explicit KDC transaction helpers (`kerberos_transaction_cache_create`, `kerberos_transaction_send/recv`, `kerberos_transaction`), multi-secret callback `kerberos_kinit_passwords_ext_cb`, `add_sockaddr_unique`, `print_canonical_sockaddr_with_port`, `get_kdc_ip_string`, and platform-specific `get_enctypes`.

## Control Flow and Behavior
`kerberos_kinit_generic_once` initializes a Kerberos context, optionally applies time offset, resolves the supplied ccache, parses the principal, configures get-init-creds options including renewable lifetime, forwardable tickets, canonicalization, optional PAC request, and optional NetBIOS address, calls a supplied credential callback, stores returned TGT credentials in the ccache, and returns canonical principal/realm and NTSTATUS mapping. `kerberos_kinit_passwords_ext` optionally builds an explicit KDC transaction cache, then tries each supplied password or NT hash until success or a non-preauth failure. With explicit KDC and `krb5_init_creds_step`, it drives the AS exchange itself over a tevent TCP stream, writing a 4-byte length-prefixed request and reading a length-prefixed reply.

## State and Persistence
The kinit paths write to a named Kerberos credential cache supplied by the caller. `ads_kdestroy` destroys that cache. `create_local_private_krb5_conf_for_domain_internal` creates `lock_path("smb_krb5")`, writes a temporary private krb5 config with realm/KDC/enctype settings, atomically renames it to `krb5.conf.<domain>`, and sets `KRB5_CONFIG` in the process environment. Optional compile-time `OVERWRITE_SYSTEM_KRB5_CONF` can symlink `/etc/krb5.conf`, which is intentionally marked as extreme legacy behavior.

## Dependencies and Integration Points
It depends on Kerberos libraries (MIT/Heimdal branches), Samba Kerberos wrappers, netlogon ping, KDC DNS discovery, secrets and loadparm settings, `tevent`, `tstream`, `tsocket`, local lock paths, and negative connection cache helpers. It integrates with domain join, machine-account authentication, password changes, PAC retrieval, and keytab refresh.

## Risks and Edge Cases
The prompter deliberately refuses new-password prompts to avoid library loops on expired keys. Explicit-KDC support requires `HAVE_KRB5_INIT_CREDS_STEP`; without it, explicit KDC is rejected. The multi-secret path uses a memory keytab for NT hash authentication with RC4-HMAC and must handle weak crypto policy elsewhere. `get_kdc_ip_string` relies on network pings and negative connection cache propagation, so generated configs can omit temporarily blacklisted DCs. Private `krb5.conf` creation changes process-global `KRB5_CONFIG`, affecting subsequent Kerberos operations. Tests should include MIT and Heimdal builds, wrong password vs preauth failure iteration, NT hash fallback, explicit KDC timeout, ccache errors, config generation with DNS lookup enabled/disabled, IPv6 KDC formatting, weak-crypto/enctype settings, and atomic rename failure paths.
