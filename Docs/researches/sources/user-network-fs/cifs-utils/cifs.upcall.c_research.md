<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.c -->
# sources/user-network-fs/cifs-utils/cifs.upcall.c

## Purpose

`cifs.upcall.c` implements the CIFS request-key helper for Kerberos/SPNEGO session setup and legacy DNS resolver keys. It decodes kernel key descriptions, switches to the initiating process namespace when requested, obtains Kerberos service tickets or uses GSSAPI/gssproxy, packages session key plus SPNEGO security blob, and instantiates the kernel key.

## Important APIs, Types, and Functions

Important types are `sectype_t`, `struct namespace_file`, and `struct decoded_args`. Major functions include `trim_capabilities`, `drop_all_capabilities`, `get_tgt_time`, `switch_to_process_ns`, `get_cachename_from_process_env`, `get_existing_cc`, `init_cc_from_keytab`, `check_service_ticket_exists`, `cifs_krb5_get_req`, `cifs_gss_get_req`, `handle_krb5_mech`, `decode_key_description`, `setup_key`, `cifs_resolver`, `ip_to_fqdn`, `lowercase_string`, and `main`.

## Control Flow

`main` parses options such as `--no-env-probe`, `--trust-dns`, `--legacy-uid`, `--krb5conf`, `--keytab`, and `--expire`, then describes the key. Resolver keys are handled immediately by `cifs_resolver`, which resolves a hostname and instantiates an IP-address key with a timeout. SPNEGO keys are decoded in a low-privilege child into shared memory, validated for required host/version/sec fields, and checked against `CIFS_SPNEGO_UPCALL_VERSION`. The helper chooses `creduid` unless legacy mode forces `uid`, optionally switches to the application process namespaces, trims capabilities, sets gid/uid, probes the initiating environment for `KRB5CCNAME`, initializes Kerberos, obtains an existing credential cache or keytab-backed memory cache, then attempts a service ticket for the supplied host. If direct host lookup fails it may try a canonical FQDN and, with `--trust-dns`, reverse-resolve the supplied IP. Successful Kerberos data is packed into `struct cifs_spnego_msg` and instantiated.

## State and Persistence Behavior

Process state includes global `krb5_context`, transient credential cache handles, talloc `DATA_BLOB`s, key description buffers, namespace file descriptors, and shared-memory decoded arguments. Persistent effects are kernel key instantiation, DNS resolver key timeout, and optional use of credential caches. The helper scrapes `/proc/<pid>/environ` only before dropping uid and avoids env probing for uid 0.

## Dependencies and Integration Points

It depends on keyutils, MIT/Heimdal Kerberos, GSSAPI/Kerberos extensions, optional libcap-ng, `/proc` namespaces and environment files, passwd/group NSS, syslog, `data_blob.h`, `spnego.h`, and `cifs_spnego.h`. It is invoked by request-key for `cifs.spnego`, `cifs.resolver`, or `dns_resolver`-style descriptions.

## Risks and Edge Cases

This is security-sensitive setuid/capability-adjacent code. Namespace switching, env scraping, credential-cache selection, and uid/gid changes must occur in the intended order. `get_cachename_from_process_env` reads attacker-controlled environment strings and must stay bounded. DNS trust mode can be unsafe if reverse DNS is compromised. There is an apparent error-path condition `if (rc != 0 && key == 0)` before negating keys; if `key` is nonzero on normal request-key failures, this condition may not negate as intended. GSSAPI lucid context handling depends on Kerberos implementation support.

## Test Signals

Strong signals include request-key integration for `cifs.spnego` and DNS resolver keys, Kerberos cache and keytab flows, gssproxy flow with `GSS_USE_PROXY`, container namespace tests, uid versus creduid tests, malformed key descriptions, long host/user fields, reverse-DNS fallback, and key instantiation/negative-instantiation behavior. Static analysis should cover privilege drop ordering and buffer bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.c -->
