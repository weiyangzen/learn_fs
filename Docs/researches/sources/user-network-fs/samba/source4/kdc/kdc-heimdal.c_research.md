# sources/user-network-fs/samba/source4/kdc/kdc-heimdal.c

## Purpose
`kdc-heimdal.c` starts and wires Samba's in-process Heimdal KDC service. It binds KDC and kpasswd sockets, processes Kerberos packets through Heimdal, initializes the Samba HDB backend and KDC plugins after fork, and registers an IRPC PAC validation endpoint.

## Important APIs, Types, And Functions
The public service initializer is `server_service_kdc_init`. Static control points are `kdc_process`, `kdc_startup_interfaces`, `kdc_check_generic_kerberos`, `kdc_task_init`, and `kdc_post_fork`. It uses `struct kdc_server` from `kdc-server.h` and an external `krb5plugin_kdc_ftable kdc_plugin_table`.

## Control Flow
`kdc_task_init` rejects non-AD-DC roles, loads interfaces, creates `struct kdc_server`, and calls `kdc_startup_interfaces` to bind KDC and kpasswd sockets. `kdc_post_fork` initializes Kerberos, retrieves Heimdal KDC config, enforces Samba-specific security defaults such as strongest keys, PAC requirement, FAST settings, and disabled armored PA-ENC-TIMESTAMP, creates the Samba HDB DB, detects RODC status, registers HDBGET/keytab and KDC plugins, initializes PKINIT, and registers `KDC_CHECK_GENERIC_KERBEROS` IRPC. `kdc_process` updates KDC time/current NT time, calls `krb5_kdc_process_krb5_request`, and maps `HDB_ERR_NOT_FOUND_HERE` to `KDC_PROXY_REQUEST`.

## State And Persistence Behavior
Runtime state is held in `struct kdc_server`: task pointer, Kerberos context, base DB context, HDB DB context, RODC flag, proxy timeout, kpasswd keytab name, and Heimdal KDC config in `private_data`. Persistent state is accessed through the Samba HDB backend, not directly here. The current NT time pointer is updated for each packet so DB glue and gMSA logic see request time.

## Dependencies And Integration Points
It integrates Samba process services, interface enumeration, tsocket addresses, Heimdal KDC/HDB, Samba HDB glue, kpasswd service, PAC validation, DSDB RODC detection, IRPC, and plugin registration. `kdc-server.c` supplies socket I/O and proxy handling; `db-glue.c` supplies HDB lookups.

## Risks
Startup ordering is critical: sockets are bound before post-fork DB/plugin setup, but request processing depends on post-fork state. Security-sensitive config defaults such as `require_pac`, strongest key flags, FAST cookie behavior, and krbtgt key strength must not regress. RODC proxy signaling depends on preserving `HDB_ERR_NOT_FOUND_HERE` from HDB to `KDC_PROXY_REQUEST`.

## Test Signals
Signals include service role gating, interface binding, KDC and kpasswd socket startup, Heimdal plugin registration, PKINIT initialization, PAC validation IRPC, RODC proxy requests, FAST/PAC behavior, and packet processing over UDP/TCP through `kdc-server.c`.
