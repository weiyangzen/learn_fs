# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.h

## Purpose

`pyrpc_util.h` declares the helper API used by hand-written and generated Python DCE/RPC extension modules.

## Important APIs, Types, and Functions

It defines `PyErr_FromNdrError` and `PyErr_SetNdrError` macros, function pointer typedefs `py_dcerpc_call_fn`, `py_data_pack_fn`, and `py_data_unpack_fn`, and `struct PyNdrRpcMethodDef`, which maps a Python method name/docstring to a generated C RPC call, packer, unpacker, opnum, and interface table. It declares all conversion, connection, method-registration, union, pointer, and error helpers implemented in `pyrpc_util.c`.

## Control Flow

There is no runtime flow. The header is consumed at compile time by generated `py_*.c` modules so they can register RPC methods and delegate common connection/call behavior.

## State and Persistence Behavior

The header itself stores no state, but it defines contracts around talloc-backed Python objects and DCE/RPC binding handles. `PyNdrRpcMethodDef` entries are generally static tables in generated modules.

## Dependencies and Integration Points

It includes `pyrpc.h` and references `struct ndr_interface_table`, `struct ndr_syntax_id`, Python object types, and DCE/RPC binding handles. It is integrated through the `pyrpc_util` build subsystem and many generated Python RPC modules.

## Risks and Test Signals

Risks include generated-code ABI drift if typedefs or struct fields change, macro error objects not setting exceptions unless used correctly, and mismatched opnums/table entries causing wrong request struct sizes. Test signals are clean generated-module compilation and runtime calls for multiple generated interfaces using the shared method table path.
