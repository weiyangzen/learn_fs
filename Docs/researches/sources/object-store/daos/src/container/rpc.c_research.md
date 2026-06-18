# sources/object-store/daos/src/container/rpc.c

Purpose: DAOS container RPC serialization and protocol-format registration definitions.

Important APIs/types/functions: custom serializers `crt_proc_struct_rsvc_hint`, `crt_proc_daos_epoch_range_t`, `crt_proc_daos_obj_id_t`, wrappers for `cont_op` inputs/outputs, many `CRT_RPC_DEFINE` declarations for v8/v9 container operations, and exported `cont_proto_fmt_v8`/`cont_proto_fmt_v9`.

Control flow: CART serialization macros generate encode/decode routines for container RPC request/reply structs. The `X` macro populates protocol RPC format arrays from `CONT_PROTO_CLI_RPC_LIST(version)` and `CONT_PROTO_SRV_RPC_LIST`. `cli.c` selects and registers one of the exported protocol formats during `dc_cont_init`.

State/persistence: no persistent state. It defines wire schemas and static protocol format arrays for the container module.

Dependencies/integration: `daos/rpc.h`, `rpc.h` sequence macros, CART protocol registration, DAOS container module opcode base, and client/server RPC list macros.

Risks: protocol compatibility depends on keeping v8/v9 sequence macros and RPC list ordering consistent with server handlers. Serializer helper failures map to `-DER_HG`, so field additions must be reflected in sequence macros and helpers.

Test signals: no direct test. Compatibility tests should verify mixed-version client/server RPC registration, encode/decode of changed fields, and every operation in the protocol list.
