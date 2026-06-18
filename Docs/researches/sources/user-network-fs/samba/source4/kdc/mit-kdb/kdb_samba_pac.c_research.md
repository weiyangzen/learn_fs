## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_pac.c

Purpose: key-data copy helpers for MIT KDB plugin. Despite the filename, this file handles decrypt/encrypt of KDB key data in Samba's no-master-key model.

Important APIs and functions: `kdb_samba_dbekd_decrypt_key_data()` copies key bytes and optional salt from `krb5_key_data` into `krb5_keyblock`/`krb5_keysalt`. `kdb_samba_dbekd_encrypt_key_data()` copies a keyblock and optional salt into `krb5_key_data`, sets version/kvno/type metadata, and does no cryptographic wrapping.

Control flow: each allocation failure returns `ENOMEM`; partial allocations are freed on immediate failure paths.

State and persistence: the functions copy transient key buffers between MIT representations. Durable storage is still Samba DSDB/SDB.

Dependencies and integration: called by MIT KDB when it needs key material in standard MIT forms. Works in tandem with dummy master-key functions.

Risks: because data is copied unencrypted, memory hygiene and caller free paths matter. Multi-slot key-data assumptions are limited to current key and optional salt at index 1.

Test signals: key data with and without salt, allocation-failure injection, kvno preservation, and freeing decrypted key contents without leaks.
