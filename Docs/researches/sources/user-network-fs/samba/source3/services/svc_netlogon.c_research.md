# sources/user-network-fs/samba/source3/services/svc_netlogon.c

Purpose: internal Service Control Manager facade for Samba's Netlogon service.

Important functions and APIs: `netlogon_status()` zeroes a `SERVICE_STATUS`, reports type `SERVICE_TYPE_WIN32_SHARE_PROCESS`, accepts no controls, and sets state to running if `lp_servicenumber("NETLOGON")` exists, otherwise stopped. `netlogon_stop()` returns status and denies access. `netlogon_start()` returns `WERR_SERVICE_DISABLED` when the share/service is absent and otherwise denies access. Exports `SERVICE_CONTROL_OPS netlogon_svc_ops`.

Control flow: all svcctl operations are simple synchronous status or denial paths; no process is started or stopped.

State and persistence: reads Samba loadparm service configuration. It does not modify persistent or runtime service state.

Dependencies and integration: depends on `lp_servicenumber`, `SERVICE_STATUS`, SVCCTL constants, and the svcctl dispatch table. Tested indirectly by RPC svcctl/netlogon torture suites registered in `selftest/tests.py`.

Risks and test signals: service state is tied to whether `NETLOGON` is configured, not a live daemon state. Clients expecting Windows-like start/stop behavior receive access denied. Test signals are correct SCM status and error codes from svcctl RPC calls.
