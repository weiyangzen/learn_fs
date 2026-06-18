# sources/user-network-fs/samba/source3/services/svc_winreg.c

Purpose: internal Service Control Manager facade for the winreg service.

Important functions and APIs: `winreg_stop()` and `winreg_start()` always return `WERR_ACCESS_DENIED`. `winreg_status()` zeroes the status, reports type `SERVICE_TYPE_WIN32_SHARE_PROCESS`, accepts no controls, and always reports `SVCCTL_RUNNING`. Exports `SERVICE_CONTROL_OPS winreg_svc_ops`.

Control flow: all operations are synchronous and side-effect free. The service is modeled as always running but not controllable by clients.

State and persistence: no local state or persistent storage. Status is constant.

Dependencies and integration: part of the svcctl service table and related to the registry service glue in `svc_winreg_glue.c`. RPC tests `rpc.winreg`, `rpc.samba3.winreg`, and `rpc.svcctl` registered in `selftest/tests.py` exercise this surface indirectly.

Risks and test signals: fixed running status can diverge from actual registry RPC availability if other subsystems fail. Expected SCM behavior is access denied for start/stop and running status for queries.
