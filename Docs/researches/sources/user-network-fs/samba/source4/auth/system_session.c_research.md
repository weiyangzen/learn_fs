# sources/user-network-fs/samba/source4/auth/system_session.c

Purpose: constructs synthetic privileged, domain-admin, and anonymous session identities without reading SAMDB user objects.

Important APIs: `system_session()` returns a static unfreeable SYSTEM session. `auth_system_session_info()` builds SYSTEM session info and attaches pending machine-account credentials. `auth_system_user_info_dc()` creates SYSTEM DC user info. `admin_session()` creates a synthetic Administrator token for a supplied domain SID. `auth_anonymous_session_info()` and `auth_anonymous_user_info_dc()` create anonymous session/user info.

Control flow: synthetic `auth_user_info_dc` structures are populated with well-known or domain-derived SIDs, zeroed 16-byte session keys, display/logon path fields, account flags, and user flags. They are converted through `auth_generate_session_info()` with privilege/default/authentication flags appropriate to the identity. SYSTEM and anonymous sessions allocate configured `cli_credentials`.

State/dependencies/integration: no durable state. `system_session()` caches a process-lifetime `auth_session_info` and prevents freeing via destructor. Depends on security SID constants, credential helpers, loadparm names/workgroup, and `auth_session` token creation. Used by internal services, SAMDB access, CLDAP startup, and tests.

Risks/test signals: synthetic tokens carry high privilege and bypass SAMDB lookup, so SID composition and static-session immutability matter. CLDAP in this subset uses `system_session()` to open SAMDB.
