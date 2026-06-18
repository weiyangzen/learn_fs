# sources/user-network-fs/samba/source4/dsdb/tests/python/key_credential_link.py

Purpose: this ACL suite validates access checks and constraints around writes to `msDS-KeyCredentialLink`, especially differences between normal Write Property and the validated write for computer objects.

Important APIs/types/functions: `AclTests` sets strict checking, opens admin `SamDB`, configures `dSHeuristics` for attribute authorization on LDAP add and owner rights behavior, and supplies credential/connection helpers. `AclKeyCredentialLinkTests` creates a user and computer, generates RSA public keys, builds `KeyCredentialLinkDn` values with `key_credential_link.create_key_credential_link()`, and exercises `_test_key_cred_link()`. Tests cover add, delete, replace, multiple values, malformed values, self vs other-object writes, computer vs user targets, and expected `ERR_INSUFFICIENT_ACCESS_RIGHTS` or `ERR_CONSTRAINT_VIOLATION`.

Control flow: setup deletes/recreates fixed test user/computer, sets the computer password, and opens user/computer-bound SamDB connections. Each test applies allow or deny ACEs for the schema attribute Write Property and validated write GUID, then attempts an LDB modify with `FLAG_MOD_ADD`, `FLAG_MOD_REPLACE`, or `FLAG_MOD_DELETE`.

State and persistence behavior: the suite mutates `dSHeuristics`, object DACLs, test users/computers, passwords, and `msDS-KeyCredentialLink` values. Cleanup restores `dSHeuristics`, deletes admin connection helpers, and force-deletes the test objects in `tearDown()`.

Dependencies and integration points: depends on Samba DSDB GUID constants, `BinaryDn`, key credential link helpers, `cryptography` RSA key generation, sealed GENSEC credentials, no-Kerberos user binds, and `SDUtils` DACL manipulation.

Risks: fixed object names can conflict with concurrent runs. DACL changes are layered during tests and rely on object deletion for cleanup. RSA generation adds CPU cost. A module-level `ldb = SamDB(...)` creates an extra admin connection outside the test classes and is not otherwise used.

Test signals: expected success/failure of LDAP modify operations under precise ACE combinations. The key behavioral signal is that Write Property permits broad mutation, while validated write is constrained to computer self-write, one value, valid format, no existing value, and no user/non-computer target.
