# sources/user-network-fs/samba/source3/auth/check_samsec.c

## Purpose
This file performs actual local SAM/passdb password verification and account policy enforcement. It validates hashes/responses, checks account restrictions, updates bad-password state, and returns server info for successful local SAM authentication.

## Important APIs, Types, and Functions
Internal helpers are `sam_password_ok`, `logon_hours_ok`, `sam_account_ok`, and `need_to_increment_bad_pw_count`. Public functions are `check_sam_security` and `check_sam_security_info3`.

## Control Flow
`check_sam_security` loads the `samu` record, rejects locked accounts early, verifies the supplied password using hash or NTLM response checks, reloads the account under a per-user named mutex, updates login attempts and bad-password counters, enforces account restrictions only after password success, resets bad counters on success, then calls `make_server_info_sam` and attaches session keys. `check_sam_security_info3` wraps this and converts server info to SamInfo3.

## State and Persistence
This file mutates passdb state: login attempt metadata, bad password count/time, and possibly lockout-related fields via passdb backend calls. The named mutex `check_sam_security_mutex_<user>` protects concurrent updates. It also flushes `PDB_GETPWSID_CACHE` after each authentication to avoid unbounded cache growth.

## Dependencies and Integration Points
Dependencies include passdb, libcli auth password-check routines, memcache, account policy APIs, named mutexes, server-info conversion, and Samba debug/logging. It is called by SAM auth modules and winbind helper paths needing local SamInfo3.

## Risks and Test Signals
Risks include race conditions around lockout updates, history-password handling that suppresses bad-count increments, policy ordering mistakes, null-password behavior, and trust-account logon-parameter enforcement. Tests should cover correct and wrong passwords, password history, disabled/locked/expired accounts, logon hours, workstation restrictions, trust account flags, bad-count reset, lockout under concurrency, and cache flush behavior.
