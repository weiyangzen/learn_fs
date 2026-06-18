# sources/user-network-fs/samba/source4/librpc/rpc/pyrpc_util.c

## Purpose

`pyrpc_util.c` provides reusable Python binding helpers for generated Samba DCE/RPC modules. It initializes DCE/RPC interface objects, connects IRPC or network pipes, creates secondary contexts, dispatches generated RPC methods, maps errors, and converts NDR/talloc objects to Python.

## Important APIs, Types, and Functions

Important exports are `py_check_dcerpc_type()`, `py_dcerpc_interface_init_helper()`, `PyInterface_AddNdrRpcMethods()`, `py_dcerpc_syntax_init_helper()`, `PyErr_SetDCERPCStatus()`, `py_return_ndr_struct()`, `PyString_FromStringOrNULL()`, `PyBytes_FromUtf16StringOrNULL()`, `PyUtf16String_FromBytes()`, `pyrpc_import_union()`, `pyrpc_export_union()`, `py_dcerpc_ndr_pointer_deref()`, and `py_dcerpc_ndr_pointer_wrap()`. The local `pyrpc_irpc_connect()` creates an IRPC binding handle from a messaging context.

## Control Flow

Interface initialization parses Python arguments for binding, loadparm, credentials, timeout, basis connection, and exception behavior. It initializes DCE/RPC, allocates the Python object, then chooses IRPC binding, secondary connection/context from a basis `ClientConnection`, or a fresh `dcerpc_pipe_connect()`. Generated method calls use `PyNdrRpcMethodDef`: pack Python args into an NDR request struct, call the generated C client function against the binding handle, and unpack the output into Python.

## State and Persistence Behavior

The helper owns each Python object's talloc context and event context references. It may create messaging clients for IRPC and install synchronous event handling on IRPC binding handles. Basis connections share underlying event/pipe references or open secondary pipes. No disk state is written.

## Dependencies and Integration Points

Dependencies include Python C API, pytalloc, pyparam, pycredentials, DCE/RPC core, messaging/IRPC, generated NDR interface tables, and generated Python marshalling code. `wscript_build` builds this as the `pyrpc_util` Python embedding subsystem used by many generated modules.

## Risks and Test Signals

Risks include Python/talloc lifetime coupling, accepting credentials without loadparm for basis connections, IRPC nested event loops, unchecked `PyDict_SetItemString()` failure in method injection, and UTF-16 byte validation edge cases. Tests should import generated modules, connect fresh and via basis connections, exercise IRPC bindings, call generated methods with result-exception behavior on/off, convert NULL strings, validate UTF-16 odd/embedded-null rejection, and import/export discriminated unions.
