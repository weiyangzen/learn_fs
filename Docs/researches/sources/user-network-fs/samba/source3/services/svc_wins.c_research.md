# sources/user-network-fs/samba/source3/services/svc_wins.c

Purpose: internal Service Control Manager facade for Samba's WINS service.

Important functions and APIs: `wins_status()` zeroes status, reports `SERVICE_TYPE_WIN32_OWN_PROCESS`, accepts no controls, and reports running only when `lp_we_are_a_wins_server()` is true; otherwise it reports stopped with `WERR_SERVICE_NEVER_STARTED`. `wins_stop()` refreshes status and denies access. `wins_start()` always denies access. Exports `wins_svc_ops`.

Control flow: status is a direct projection of configuration; start and stop do not mutate state.

State and persistence: reads loadparm WINS-server configuration but performs no writes.

Dependencies and integration: used by svcctl RPC service enumeration/control paths. It depends on SVCCTL constants and loadparm WINS helper state.

Risks and test signals: a configured WINS server is considered running regardless of deeper daemon health. Expected tests should assert status reflects configuration and start/stop return access denied.
