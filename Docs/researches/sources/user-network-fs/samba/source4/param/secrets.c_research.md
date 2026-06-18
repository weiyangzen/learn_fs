# sources/user-network-fs/samba/source4/param/secrets.c

Purpose: `secrets.c` provides helpers for opening Samba's secrets LDB and extracting domain SID/keytab-related data.

Important APIs, types, and functions: It implements `secrets_db_create`, `secrets_db_connect`, `secrets_get_domain_sid`, and `keytab_name_from_msg`.

Control flow: Database helpers call `ldb_wrap_connect` for `secrets.ldb`, with or without `LDB_FLG_DONT_CREATE_DB`. `secrets_get_domain_sid` opens the database, searches under `cn=Primary Domains` for the flatname, fetches `objectSid` and optionally `secureChannelType`, pulls the SID with NDR, and returns an allocated `dom_sid`. `keytab_name_from_msg` prefers `krb5Keytab`; otherwise it converts `privateKeytab` to an LDB-relative file path and prefixes `FILE:`.

State and persistence behavior: The helpers open persistent `secrets.ldb` but only read in this file. Returned SIDs and strings are talloc-owned by the caller.

Dependencies and integration points: It depends on loadparm private paths through ldbwrap, DSDB search helpers, NDR security parsing, and LDB message APIs. Provisioning and authentication code use these helpers.

Risks: Search failures and missing attributes return NULL with error strings; callers must not conflate missing domain with parse corruption. The function does not free the LDB context on all success paths because it is talloc-parented under the caller context.

Test signals: Tests should cover create/connect flags, missing database, absent domain, malformed SID blob, missing secureChannelType when requested, and keytab selection precedence.
