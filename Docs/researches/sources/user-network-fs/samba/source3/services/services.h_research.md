# sources/user-network-fs/samba/source3/services/services.h

Purpose: shared declarations for Samba's source3 service-control implementation, including service operation dispatch and service handle metadata.

Important types and APIs: includes generated `svcctl.h`. Defines `SVCCTL_SCRIPT_DIR` as `svcctl`. `SERVICE_CONTROL_OPS` contains function pointers for `stop_service`, `start_service`, and `service_status`, all returning `WERROR` and using `struct SERVICE_STATUS`. `SERVICE_INFO` stores handle type, service name, granted access mask, and the operations table. Handle type constants distinguish SCM, service, and database lock handles.

Control flow: header-only; control flow is supplied by service implementation files and the svcctl server dispatch that invokes the function pointers.

State and persistence: `SERVICE_INFO` instances carry per-handle state in memory. No persistent state is declared here.

Dependencies and integration: consumed by internal service implementations such as `svc_netlogon.c`, `svc_spoolss.c`, `svc_winreg.c`, `svc_wins.c`, and `svc_rcinit.c`, and by the RPC service-control server.

Risks and test signals: function pointer signatures are ABI-sensitive within source3. Mis-set handle type constants or access masks can expose incorrect service-control behavior. RPC svcctl torture tests in `selftest/tests.py` are the broad integration signal.
