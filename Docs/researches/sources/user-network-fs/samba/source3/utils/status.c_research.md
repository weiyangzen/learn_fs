# sources/user-network-fs/samba/source3/utils/status.c

## Purpose

`sources/user-network-fs/samba/source3/utils/status.c` implements `smbstatus`, Samba's live status-reporting command. It reports active sessions, tree connections, open files/share modes, byte-range locks, notify registrations, and profiling information in either text or JSON mode. The source was read as a complete 1341-line file.

## Important APIs, Types, and Functions

Important functions include `main`, `prepare_sessionid`, `traverse_sessionid`, `prepare_connections`, `traverse_connections`, `prepare_share_mode`, `print_share_mode`, `prepare_brl`, `print_brl`, `prepare_notify`, `print_notify_rec`, `session_dialect_str`, crypto helpers `smbXsrv_is_encrypted`, `smbXsrv_is_partially_encrypted`, `smbXsrv_is_signed`, `smbXsrv_is_partially_signed`, and user filters `Ucrit_addUid`, `Ucrit_checkUid`, `Ucrit_addPid`, `Ucrit_checkPid`. It shares `struct traverse_state` and `enum crypto_degree` with `status.h`.

## Control Flow

`main` initializes Samba command-line parsing, default log level, security, optional Jansson root JSON, and root-only messaging context. It parses flags for process/share/lock/notify/profile/brief/numeric/json/fast/resolve-uids. Profile-only modes call `status_profile_dump` or `status_profile_rates`. Otherwise it traverses session records with `sessionid_traverse_read`, connection records with `connections_forall_read`, share-mode records with `share_entry_forall_read`, optional byte-range locks with `brl_forall`, and notify records with `notify_walk`.

## State and Persistence Behavior

The file reads persistent/live Samba databases but does not mutate them: session DB, connection TDB, `locking.tdb`, share-mode locks, leases DB, notifyd DB, messaging context, and profile shared memory. User filtering stores one uid and up to `SMB_MAXPIDS` matching server IDs in static globals so later share/lock views can be limited to the selected user's processes.

## Dependencies and Integration Points

It integrates with `session.h`, locking/share-mode APIs, `conn_tdb`, `serverid`, leases DB, notifyd, messaging, profile support, loadparm/cmdline contexts, and JSON/profile helper modules. JSON output calls `status_json.c`; when Jansson is absent, JSON is rejected at runtime.

## Risks and Edge Cases

The command requires real root and rejects setuid use. `--fast` disables process-existence checks, so stale records may appear. Unknown share deny modes and unknown crypto/signing ciphers can produce warnings or error status. User filtering has a hard `SMB_MAXPIDS` limit. Several traversal callbacks return errors only through integer status while the top-level flow often continues, so partial data or truncated lock lists are possible.

## Test Signals

Tests should exercise text and JSON output, root/setuid rejection, process-only/share-only/lock-only/brief combinations, stale process filtering versus `--fast`, user filtering, crypto/signing degree formatting, share-mode and lease display, byte-range lock traversal, notify output, and no-`locking.tdb` behavior.
