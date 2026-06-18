# sources/user-network-fs/samba/source4/kdc/kdc-service-mit.c

## Purpose
`kdc-service-mit.c` starts a MIT Kerberos `krb5kdc` child process inside Samba AD DC mode and initializes Samba's kpasswd service using MIT KDB/keytab facilities.

## Important APIs, Types, And Functions
The main exported service initializer is `mitkdc_task_init`; `server_service_mitkdc_init` registers it under the `kdc` service name. Static helpers include `kdc_server_destroy`, `startup_kpasswd_server`, and `mitkdc_server_done`.

## Control Flow
`mitkdc_task_init` rejects standalone/member roles, loads interfaces, sets `KRB5_KDC_PROFILE` from the private dir, optionally sets `KRB5_TRACE`, launches the configured MIT KDC command with `samba_runcmd_send`, installs an IRPC service, allocates `struct kdc_server` and base context, initializes Samba/MIT krb5 and kadm5 contexts, opens a kadm5 server handle, registers MIT KDB keytab support, sets the kpasswd keytab to `KDB:`, and binds kpasswd sockets. If the child process exits, `mitkdc_server_done` terminates the task.

## State And Persistence Behavior
The MIT KDC itself is a child process; this parent task tracks it and owns the kpasswd socket/service state. `kdc->private_data` holds a kadm5 server handle and is destroyed by `kadm5_destroy`. Persistent DB access occurs through MIT KDB and Samba kpasswd password-setting paths, not directly in this file.

## Dependencies And Integration Points
It depends on Samba service/process model, interface loading, dynamic log paths, MIT kadm5/KDB APIs, `mit_kdc_irpc`, `kdc-server.c`, and the common kpasswd service. It is an alternative service path to the in-process Heimdal KDC but still uses Samba's socket/kpasswd helpers.

## Risks
Child process lifecycle is critical: a normal or abnormal MIT KDC exit terminates the Samba task. Environment variables must point at the correct generated KDC profile and trace location. The service registers as `kdc` with `inhibit_pre_fork = true` because IRPC runs only in the master event loop; changing that can break IRPC handling.

## Test Signals
Signals include AD DC role gating, MIT KDC command startup/failure, child-exit termination, IRPC service setup, kpasswd socket binding, `KDB:` keytab registration, and password-change flows through the MIT service path.
