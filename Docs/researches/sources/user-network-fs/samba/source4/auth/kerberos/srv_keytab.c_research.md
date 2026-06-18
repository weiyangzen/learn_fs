<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c -->
# sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c

Purpose: service keytab creation and update utilities for Samba AD accounts, including group Managed Service Account key extraction.

Important APIs: `keytab_add_keys()` derives keys for each enctype/principal/kvno and avoids adding exact duplicates. `smb_krb5_fill_keytab()` parses the salt principal, maps supported encryption types, adds current keys, and optionally previous keys. `smb_krb5_fill_keytab_gmsa_keys()` reads gMSA managed password data from samdb and populates a keytab with salted AES keys. `smb_krb5_update_keytab()` opens a keytab, builds principals from account/SPNs, removes obsolete entries, and fills current/previous keys. `smb_krb5_create_memory_keytab()` creates a random `MEMORY:` keytab name and delegates update.

Control flow: update resolves the keytab, uppercases realm, creates principal array, removes stale kvnos, optionally validates `saltPrincipal`, and fills the keytab unless this is delete-only mode. gMSA flow re-queries password attributes, builds temporary credentials, sets realm/username/kvno, restricts enctypes to strong salted AES, parses current and previous managed passwords, derives a salt principal, and fills one principal.

State and persistence: file keytabs are modified in place; memory keytabs persist under generated `MEMORY:<random>` names while handles remain open. Old keys may be retained for kvno-1 depending on cleanup findings and `include_historic_keys`. Principal arrays and salt principals are explicitly freed.

Dependencies and integration: uses Samba credentials, credentials_krb5, Kerberos utility functions, gMSA NDR/DSDB helpers, samdb, and Kerberos enctype conversion helpers. It supports domain exportkeytab, machine account keytab refresh, and gMSA service operation.

Risks and test signals: key derivation depends on the correct salt principal and enctype mask. gMSA intentionally drops RC4 because UTF16-munged to UTF8 conversion can corrupt RC4 password material. Tests should cover duplicate suppression, old-key retention, delete-only mode, missing salt principal, SPN plus account principal generation, gMSA missing password/kvno/enctype attributes, memory keytab creation, and error strings on failed keytab writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/srv_keytab.c -->
