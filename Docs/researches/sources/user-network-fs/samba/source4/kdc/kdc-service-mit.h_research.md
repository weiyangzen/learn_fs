# sources/user-network-fs/samba/source4/kdc/kdc-service-mit.h

## Purpose
`kdc-service-mit.h` declares the MIT KDC task initializer used when Samba is built/configured to run MIT Kerberos as the KDC backend.

## Important APIs, Types, And Functions
The only declaration is `NTSTATUS mitkdc_task_init(struct task_server *task)`, implemented in `kdc-service-mit.c`.

## Control Flow
The server service registration calls this initializer to start the MIT KDC parent task and kpasswd support. The header itself has no runtime logic.

## State And Persistence Behavior
No state is stored here. The implementation stores process and kpasswd state in `struct kdc_server`.

## Dependencies And Integration Points
It is included by service registration or build units that need the MIT KDC task entry point. It depends on Samba's `NTSTATUS` and `task_server` types being visible to the including translation unit.

## Risks
Low direct risk; prototype drift would break service registration builds. The declaration intentionally keeps the MIT service surface minimal.

## Test Signals
Build with MIT KDC support and service startup tests are the relevant signals.
