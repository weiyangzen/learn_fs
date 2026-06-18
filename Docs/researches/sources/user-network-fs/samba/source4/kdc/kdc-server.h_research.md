# sources/user-network-fs/samba/source4/kdc/kdc-server.h

## Purpose
`kdc-server.h` defines shared runtime structures and socket API for Samba KDC services.

## Important APIs, Types, And Functions
`struct kdc_server` holds task/process state, Kerberos context, Samba base/DB contexts, RODC flag, proxy timeout, kpasswd keytab name, private service data, and current DB context. `enum kdc_code_e` distinguishes normal reply, error, and proxy request. `kdc_process_fn_t` is the callback signature for KDC/kpasswd processors. `struct kdc_socket` and `struct kdc_udp_socket` hold socket-local state. `kdc_add_socket` binds service sockets.

## Control Flow
Service initializers allocate a `kdc_server`, fill contexts and callback data, then call `kdc_add_socket` with a name, address, port, processor, and UDP-only flag. Runtime packet processing is implemented in `kdc-server.c`.

## State And Persistence Behavior
The header defines in-memory server and socket state only. Persistent Kerberos/AD data lives behind `samba_kdc_db_context` and the service-specific private data.

## Dependencies And Integration Points
It is included by Heimdal service startup, MIT kpasswd startup, socket handling, proxy handling, and kpasswd service code. It depends on Samba task server types, tsocket addresses, Heimdal/Samba Kerberos context types, and process model operations.

## Risks
Changes to `struct kdc_server` affect many service files. The `private_data` field carries different types depending on Heimdal versus MIT paths, so users must cast carefully. The `kdc_process_fn_t` return code controls RODC proxy behavior.

## Test Signals
Build coverage catches signature/struct drift. Runtime signals are successful socket registration from both Heimdal and MIT service initializers, plus correct processing of `KDC_OK`, `KDC_ERROR`, and `KDC_PROXY_REQUEST`.
