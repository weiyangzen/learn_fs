## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_masterkey.c

Purpose: MIT KDB master-key compatibility shim. Samba does not use a MIT master key to encrypt principal keys, so this file supplies dummy success responses where MIT requires master-key APIs.

Important APIs and functions: `kdb_samba_fetch_master_key()` returns success without populating a real key. `kdb_samba_fetch_master_key_list()` allocates a single `krb5_keylist_node` with `ENCTYPE_UNKNOWN` and kvno 1.

Control flow: only allocation failure returns `ENOMEM`; otherwise the dummy list is returned.

State and persistence: no persistent key material. This reinforces that Samba key material is stored and protected by DSDB mechanisms, not MIT KDB master-key wrapping.

Dependencies and integration: used by the MIT KDB function table and key-data decrypt/encrypt shims.

Risks: MIT features expecting real master-key rotation or validation are not supported. The dummy key must be acceptable to the MIT code paths Samba uses.

Test signals: KDC startup, principal key decrypt/encrypt paths, and kadmind operations that ask for master-key lists.
