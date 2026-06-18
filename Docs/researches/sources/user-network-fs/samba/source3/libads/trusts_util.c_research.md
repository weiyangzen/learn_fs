# sources/user-network-fs/samba/source3/libads/trusts_util.c

## Purpose

`trusts_util.c` manages trust account password changes over NETLOGON, including password generation, local secrets staging/recovery, remote verification with current/old passwords, Kerberos-authenticated secure-channel cases, and final local/remote commit handling.

## Important APIs, Types, and Functions

`trust_pw_new_value` generates a random machine/trust password sized by secure channel type and security mode. `trust_pw_change` performs the full password rotation. Internal helpers include `trust_pw_change_state_destructor` for g_lock cleanup, `netlogon_creds_cli_lck_auth` to authenticate under an exclusive NETLOGON creds lock, and `extract_nt_hash_and_pwd` to convert stored UTF-16MUNGED secrets into UTF-8 cleartext plus NT hash pointers.

## Control Flow

`trust_pw_change` takes an exclusive g_lock per domain, loads trust credentials, determines secure-channel type, password age, old kvno, and whether a change is needed. For workstation/BDC channels it calls `secrets_prepare_password_change`, handles any previous unfinished change, and builds a list of candidate current/old/older passwords. For domain trust channels it uses passdb trusted-domain state and increments the trust version.

Before changing anything remotely, it authenticates to the DC using all candidate hashes, or performs Kerberos kinit against an explicit KDC if the NETLOGON credential state is Kerberos-authenticated. If a previous staged password is already accepted remotely, it finishes recovery. If only an older password works, it defers the change. Otherwise it writes the new password locally, calls `netlogon_creds_cli_ServerPasswordSet`, records failed/deferred state depending on connection status, finishes local secrets on success, updates in-memory credentials, and verifies the new password remotely.

## State and Persistence Behavior

Persistent state includes secrets database password-change records, trusted-domain passdb passwords, keytab sync side effects via `sync_pw2keytabs`, NETLOGON credential state, and optional Kerberos memory ccache used only during verification. The g_lock protects concurrent local rotations for the same domain.

## Dependencies and Integration Points

It depends on NETLOGON creds client APIs, RPC binding handles, passdb/secrets, generated secrets and netlogon NDR types, Kerberos wrappers, messaging/g_lock, loadparm machine password timeout/security role, and keytab sync when ADS is enabled. It is part of machine/trust account maintenance.

## Risks and Test Signals

Risks include incorrect recovery after interrupted local/remote commits, password length constraints for RODC/RWDC forwarding, lock acquisition failures, Kerberos path requiring an IP-address host binding, local password committed before remote rejection, deferred state persistence errors, and secret data lifetime/logging. Tests should cover timeout/force decisions, every supported secure-channel type, previous-change recovery, older-password defer, NETLOGON auth failure, Kerberos verification, disconnected versus connected remote set failure, secrets finish/fail/defer calls, keytab sync, and final new-password verification.
