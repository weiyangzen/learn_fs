# sources/user-network-fs/samba/source3/libnet/libnet_join.c

## Purpose

Implements Samba source3 domain join, offline join, join verification, unjoin, machine-secret storage, AD post-processing, keytab synchronization, and optional registry-backed configuration updates.

## Important APIs, Types, and Functions

Public APIs are `libnet_init_JoinCtx`, `libnet_init_UnjoinCtx`, `libnet_Join`, `libnet_Unjoin`, and `libnet_join_ok`. Major internal paths are `libnet_DomainJoin`, `libnet_DomainOfflineJoin`, `libnet_DomainUnjoin`, `libnet_join_joindomain_rpc`, `libnet_join_joindomain_rpc_unsecure`, ADS LDAP helpers for account/SPN/UPN/encryption-type updates, and config helpers `do_JoinConfig` and `libnet_unjoin_config`.

## Control Flow

Join pre-processing validates the target domain and machine name, parses optional `DOMAIN\DC`, and initializes secrets unless provisioning/offline mode skips them. Online join discovers a writable DC, prepares krb5 config, queries LSA domain info, checks local config, optionally precreates an AD machine account over LDAP, then joins over SAMR or unsecure Netlogon password set. Post-processing updates AD attributes, stores SAF hints, saves machine secrets, updates config, syncs keytabs, maps built-in groups, and verifies the secure channel. Offline join consumes ODJ provision data without network operations. Unjoin deletes through ADS when requested, otherwise disables through SAMR, removes local secrets, deletes SAF hints, and updates config.

## State and Persistence Behavior

Persistent effects include remote machine account creation/modification/deletion/disablement, `secrets.tdb` trust credentials, SAF DC cache entries, private krb5 config, keytab sync, registry-backed smb.conf changes, and builtin group membership setup. Failed post-join verification triggers rollback through unjoin.

## Dependencies and Integration Points

Integrates ADS LDAP, SAMR/LSA/Netlogon RPC, dsgetdcname, credentials/gensec, passdb secrets, smbconf registry backend, keytab sync, offline-join helpers, and loadparm configuration.

## Risks and Test Signals

Risks include many partial side effects, sensitive machine password handling, DC replication timing, divergence between LDAP and RPC account creation, and config mutation limited to the registry backend. Tests should cover AD and NT-style joins, unsecure joins, provision-only mode, offline join, LDAP fallback, post-verify rollback, unjoin delete/disable/no-delete modes, and config validation errors.
