# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door.h

## Scope

Complete file read, 333 lines. This header defines illumos door lightweight RPC attributes, data structures, syscall subcodes, and kernel interfaces.

## Public Surface

It defines door creation/status attributes such as `DOOR_UNREF`, `DOOR_PRIVATE`, `DOOR_REFUSE_DESC`, `DOOR_NO_CANCEL`, `DOOR_LOCAL`, `DOOR_REVOKED`, and related masks. It defines descriptor attributes `DOOR_DESCRIPTOR`, kernel-only `DOOR_HANDLE`, and `DOOR_RELEASE`, plus internal flags and parameter ids.

Non-assembly builds get:

- `door_ptr_t`, `door_id_t`, and `door_attr_t`.
- Kernel-only opaque `door_handle_t`.
- `door_desc_t`, `door_info_t`, `door_cred_t`, `door_arg_t`, 32-bit `door_arg32_t`, `door_results`, 32-bit `door_results32`, `door_return_desc_t`, and 32-bit variant.
- Kernel-only `door_node_t`, vnode conversion macros, door dispatch/revoke/fork/bind helpers, globals, and in-kernel door API functions.

It ends with door syscall subcodes: create, revoke, info, call, bind, unbind, unref, credentials, return, getparam, and setparam.

## Behavior And Integration

Doors provide process-local RPC via file descriptors or kernel handles. `door_arg_t` carries request/result data and descriptors; `door_info_t` exposes target procedure/cookie/attributes/unique id. Kernel `door_node_t` ties doors to vnodes, target process, active invocation counts, server pools, and parameter limits.

## Dependencies And Invariants

On amd64 with 32-bit alignment differences, `door_desc_t` and `door_info_t` are packed to avoid special copy conversions. `DOOR_CREATE_MASK`, `DOOR_KI_CREATE_MASK`, and `DOOR_ATTR_MASK` define accepted flag sets.

## Risks

Descriptor passing and result buffers require strict copyin/copyout validation. `door_ptr_t` stores user pointers as 64-bit integer values for ABI stability. Kernel door APIs are marked private and may change incompatibly.
