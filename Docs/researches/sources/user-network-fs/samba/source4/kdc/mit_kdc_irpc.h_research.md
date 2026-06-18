## sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.h

Purpose: small public declaration for registering MIT KDC IRPC handlers.

Important API: `samba_setup_mit_kdc_irpc(struct task_server *task)` returns NTSTATUS after setting up DB/krb5 context and IRPC registration.

Control flow and integration: included by MIT KDC server setup code so the IRPC service can be installed when running with MIT Kerberos.

State and persistence: no state; implementation stores registration context under the task.

Dependencies: requires `struct task_server` and NTSTATUS from includers.

Risks: no include guard in this header as shown; repeated inclusion in a single translation unit could redeclare harmlessly but guard consistency would be preferable.

Test signals: compile inclusion from multiple MIT KDC units and verify setup failure propagates NTSTATUS.
