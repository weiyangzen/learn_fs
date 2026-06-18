# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.c

Purpose: this file restricts Kerberos encryption types used by server gssd to those supported by the kernel, falling back to version-based defaults when the kernel does not expose a list.

Important APIs and functions: `svcgssd_limit_krb5_enctypes()` is called before accepting a security context. `svcgssd_free_enctypes()` releases global parsed/cached enctype arrays. Internal helpers `parse_enctypes()` and `get_kernel_supported_enctypes()` parse `/proc/fs/nfsd/supported_krb5_enctypes`.

Control flow: when `HAVE_SET_ALLOWABLE_ENCTYPES` is available, the code chooses default old or new kernel enctype lists based on `linux_version_code()`, reads the procfs enctype list, and calls `gss_set_allowable_enctypes(&min_stat, gssd_creds, &krb5oid, ...)`. If the kernel list is unchanged, parsing is skipped via `cached_enctypes`.

State and persistence: global `parsed_num_enctypes`, `parsed_enctypes`, and `cached_enctypes` cache the last kernel string. External state is read-only procfs capability data and the global GSS credential handle.

Dependencies and integration: depends on MIT/Heimdal Kerberos enctype constants, GSSAPI Kerberos OID definitions, nfs-utils `gss_util`, logging, and version helpers. It is integrated from `handle_nullreq()`.

Risks: parsing is permissive and uses `atoi`, so malformed comma content can become zero entries after the first digit. A failed proc read silently falls back to defaults. Test signals include kernel list parsing, cache reuse, fallback lists for old/new kernel version codes, and failure propagation from `gss_set_allowable_enctypes()`.
