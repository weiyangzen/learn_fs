# sources/user-network-fs/samba/source3/passdb/machine_account_secrets.c

## Purpose

`machine_account_secrets.c` owns Samba's local persistence for generated private identity and trust information: domain SIDs and GUIDs, machine account passwords, Kerberos salting principals, legacy trust-password hashes, and the newer NDR-encoded `secrets_domain_info1` record used for joins and password rollover. It bridges old `secrets.tdb` key/value entries with newer structured domain info so callers can continue to fetch legacy plaintext/hash secrets while upgraded paths get richer password history, Kerberos keys, and password-change state.

## Important APIs, Types, And Functions

Key string builders normalize domains with `talloc_asprintf_strupper_m()`: `domain_sid_keystr()`, `domain_guid_keystr()`, `protect_ids_keystr()`, `machine_password_keystr()`, `machine_prev_password_keystr()`, `machine_sec_channel_type_keystr()`, `machine_last_change_time_keystr()`, `trust_keystr()`, `domain_info_keystr()`, and `des_salt_key()`.

SID/GUID APIs include `secrets_store_domain_sid()`, `secrets_fetch_domain_sid()`, `secrets_delete_domain_sid()`, `secrets_store_domain_guid()`, and `secrets_fetch_domain_guid()`. Domain protection is controlled by `secrets_mark_domain_protected()` and `secrets_clear_domain_protection()`; protection prevents accidental direct SID/GUID changes except during the transaction that rewrites a full domain-info record.

Machine password compatibility APIs include `secrets_store_machine_pw_sync()`, `secrets_fetch_machine_password()`, `secrets_fetch_prev_machine_password()`, `secrets_fetch_pass_last_set_time()`, `secrets_fetch_trust_account_password_legacy()`, and `secrets_delete_machine_password_ex()`. Kerberos salt helpers are `kerberos_standard_des_salt()`, `kerberos_secrets_store_des_salt()`, `kerberos_secrets_fetch_salt_princ()`, and the private `kerberos_secrets_fetch_des_salt()`.

Structured domain-info APIs are `secrets_fetch_or_upgrade_domain_info()`, `secrets_store_JoinCtx()`, `secrets_prepare_password_change()`, `secrets_failed_password_change()`, `secrets_defer_password_change()`, and `secrets_finish_password_change()`. Internals include `secrets_fetch_domain_info1_by_key()`, `secrets_store_domain_info1_by_key()`, `secrets_store_domain_info()`, `secrets_domain_info_password_create()`, `secrets_domain_info_kerberos_keys()`, `secrets_check_password_change()`, and `secrets_abort_password_change()`.

## Control Flow And State

`secrets_store_machine_pw_sync()` writes current password, optional previous password, secure channel, last-change timestamp, domain SID, and salting principal, or deletes join state when requested. `secrets_store_domain_info()` is the transactional canonical writer: it validates role/channel, clears protection, deletes older join keys, writes the packed NDR record, writes compatibility machine-password keys, stores GUIDs, marks IDs protected, and commits. `secrets_fetch_or_upgrade_domain_info()` migrates legacy plaintext/SID/GUID state into a structured record and reparses it. Join and machine-password change flows preserve old passwords, stage `next_change`, verify cookies against stored state, and only sync keytabs after commits.

## Persistence And Secret Handling

Persistent state lives in Samba secrets storage under stable uppercase key prefixes such as `SECRETS_DOMAIN_SID`, `SECRETS_DOMAIN_GUID`, `SECRETS_MACHINE_PASSWORD`, `SECRETS_MACHINE_PASSWORD_PREV`, `SECRETS_MACHINE_LAST_CHANGE_TIME`, `SECRETS_MACHINE_SEC_CHANNEL_TYPE`, `SECRETS_MACHINE_ACCT_PASS`, `SECRETS_MACHINE_DOMAIN_INFO`, and `SECRETS_SALTING_PRINCIPAL/DES`. Structured records are NDR blobs; legacy machine password data is mostly raw strings, 32-bit little-endian integers, and fixed structs. Sensitive memory is handled with `BURN_FREE()`, `BURN_FREE_STR()`, `data_blob_clear_free()`, `talloc_keep_secret()`, hash-zeroing destructors, and constant-time hash comparisons.

## Dependencies And Integration Points

This file depends on `secrets.h`, `dbwrap`, generated NDR for secrets/join structures, libcli auth/security types, Kerberos wrappers, loadparm, server role macros, and time utilities. It is consumed by passdb and credential code that fetches machine trust credentials, by join code via `secrets_store_JoinCtx()`, by machine password rotation logic, and by SID initialization in `machine_sid.c`.

## Risks And Test Signals

High-risk areas are transaction correctness across dual-format writes, domain ID protection, preserving old passwords on rejoin, cookie/race validation during password changes, optional Kerberos key generation, and corrupted fixed-size/NDR blobs. Tests should cover legacy upgrade, delete-join cleanup, protected SID/GUID refusal, GUID lazy creation for DC roles, join writes preserving old passwords, prepare/finish/fail/defer change paths, keytab sync ordering, salt fallback, secure channel defaulting, and malformed blob sizes.
