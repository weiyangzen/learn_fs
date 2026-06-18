# sources/user-network-fs/samba/source4/param/secrets.h

Purpose: `secrets.h` declares constants and helpers for Samba's secrets database layout.

Important APIs, types, and functions: It defines DN/filter macros such as `SECRETS_PRIMARY_DOMAIN_DN`, `SECRETS_PRINCIPALS_DN`, `SECRETS_PRIMARY_DOMAIN_FILTER`, `SECRETS_PRIMARY_REALM_FILTER`, `SECRETS_KRBTGT_SEARCH`, `SECRETS_PRINCIPAL_SEARCH`, and `SECRETS_LDAP_FILTER`. It declares `randseed_init`, secrets DB open functions, `secrets_get_domain_sid`, and `keytab_name_from_msg`.

Control flow: The header is a contract for callers constructing LDB searches or opening secrets databases.

State and persistence behavior: It describes persistent records in `secrets.ldb` but stores no state itself.

Dependencies and integration points: It forward declares loadparm, tevent, LDB message/context types, and includes NDR misc types for `enum netr_SchannelType`.

Risks: Filter macros contain `%s` placeholders and must be used with proper LDB escaping. Layout constants are shared assumptions across provisioning, authentication, and RPC code.

Test signals: Compile tests and LDB integration tests should confirm filters match created secrets records and that callers escape user/domain input correctly.
