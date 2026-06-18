# sources/user-network-fs/samba/source3/services/svc_spoolss.c

Purpose: internal Service Control Manager facade for Samba's spoolss/spooler state.

Important functions and APIs: `spoolss_stop()` zeroes the status, calls `lp_set_spoolss_state(SVCCTL_STOPPED)`, fills type `SERVICE_TYPE_INTERACTIVE_PROCESS | SERVICE_TYPE_WIN32_OWN_PROCESS`, and returns OK. `spoolss_start()` refuses when `lp__disable_spoolss()` is true, returns already-running if applicable, otherwise sets state running. `spoolss_status()` reports `lp_get_spoolss_state()`. Exports `spoolss_svc_ops`.

Control flow: start/stop do not launch or kill a separate process; they mutate Samba's configured spoolss state flag. Status reads that flag.

State and persistence: state is held in loadparm/runtime spoolss state through `lp_set_spoolss_state`/`lp_get_spoolss_state`. Persistence depends on how that state is backed elsewhere; this file does not write config.

Dependencies and integration: used by svcctl RPC handling and exercised indirectly by spoolss and svcctl torture tests. It depends on loadparm spoolss helpers and SVCCTL constants.

Risks and test signals: because stop is "not really" stopping an OS service, clients may observe Windows-compatible SCM responses without real process lifecycle changes. Test signals are correct start/stop/status error codes, especially disabled and already-running cases.
