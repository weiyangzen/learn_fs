# sources/user-network-fs/samba/source3/libads/kerberos_proto.h

## Purpose
This header declares libads Kerberos helper APIs for kinit, ccache destruction, local krb5 config generation, PAC retrieval, password setting, and key derivation.

## Important APIs and Types
It defines `DEFAULT_KRB5_PORT`, forward-declares `PAC_DATA_CTR` and `samr_Password`, includes Kerberos system headers and `ads_status.h`, declares `kerberos_kinit_password_ext`, `kerberos_kinit_passwords_ext`, `ads_kdestroy`, `kerberos_kinit_password`, `create_local_private_krb5_conf_for_domain_internal`, inline wrappers for normal and join-time krb5 config creation, `kerberos_return_pac`, `ads_krb5_set_password`, `kerberos_set_password`, and `create_kerberos_key_from_string` under `HAVE_KRB5`.

## Dependencies and Integration Points
It is consumed by `authdata.c`, `krb5_setpw.c`, domain join code, and keytab/password flows. The inline wrappers encode an important policy distinction: normal configs allow DNS KDC lookup, while join-time configs disable it to avoid replication races after machine account creation.

## Risks and Test Signals
Header risk lies in conditional Kerberos type visibility and inline policy changes. Compile tests should cover Kerberos-enabled and disabled builds and ensure callers get the correct DNS lookup behavior through the two inline wrappers.
