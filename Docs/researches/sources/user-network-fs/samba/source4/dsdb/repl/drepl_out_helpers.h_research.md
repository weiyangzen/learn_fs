# sources/user-network-fs/samba/source4/dsdb/repl/drepl_out_helpers.h

Purpose: nominal header for outgoing DRS helper declarations.

Important APIs/types: in this snapshot the header only contains an include guard and no explicit declarations. The actual helper functions used by the service, such as `dreplsrv_out_drsuapi_send()`, `dreplsrv_op_pull_source_send()`, and `dreplsrv_op_pull_source_recv()`, are likely declared through generated `drepl_service_proto.h` included by `drepl_service.h`.

Control flow/state: none. This file exists to reserve/structure the helper interface but does not currently provide a compile-time contract of its own.

Dependencies/integration: included by `drepl_service.h`, so it is part of the public service include chain even while empty. Risks include reader confusion and missed prototypes if generated headers change; adding declarations here must avoid conflicts with generated prototypes. Test signals are compile-only: all DREPL translation units should still see the helper prototypes through the generated include chain.
