# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc.h

## Purpose

`pyrpc.h` is the shared header for Python DCE/RPC binding code. It defines the concrete Python object layout for client connections and a reusable type-check macro used by generated or hand-written Python RPC bindings.

## Important APIs, Types, and Functions

`PY_CHECK_TYPE(type, var, fail)` validates Python object types and emits contextual `TypeError` messages. `dcerpc_InterfaceObject` embeds `PyObject_HEAD`, a talloc memory context, `struct dcerpc_pipe *`, `struct dcerpc_binding_handle *`, `struct tevent_context *`, and a `raise_result_exceptions` boolean. The header also aliases several domain SID generated type/check names and defines `NDR_DCERPC_REQUEST_OBJECT_PRESENT` when absent.

## Control Flow

There is no runtime flow in this file. It controls compile-time structure sharing between `pyrpc.c`, `pyrpc_util.c`, and generated Python NDR/RPC modules.

## State and Persistence Behavior

The object layout defines how Python connection objects persist live RPC state across method calls. The state is memory-only and released through the deallocator in `pyrpc.c`.

## Dependencies and Integration Points

It includes Python error helpers and depends on DCE/RPC, talloc, and tevent types being visible through including translation units. Generated code relies on this exact ABI, so field changes affect Python extension compatibility.

## Risks and Test Signals

Risks include ABI breakage if the struct layout changes, macro misuse with expressions that have side effects, and type aliases drifting from generated NDR type names. Test signals are successful compilation of generated Python RPC modules, type-check failures with useful messages, and runtime connection object behavior through `samba.dcerpc.base`.
