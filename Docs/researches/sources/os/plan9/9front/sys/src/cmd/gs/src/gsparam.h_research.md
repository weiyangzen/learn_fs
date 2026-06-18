# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparam.h

Defines the client-facing parameter dictionary API used by Ghostscript objects and devices.

Key definitions:
- `gs_param_list`, `gs_param_name`, `gs_param_type`.
- Scalar, homogeneous collection, and heterogeneous collection value representations.
- `gs_param_value` union and `gs_param_typed_value`.
- Collection mode enum for normal dictionaries, integer-key dictionaries, and arrays.
- `gs_param_enumerator_t` and `gs_param_key_t`.
- `gs_param_list_procs`, the polymorphic operation table for typed transmission, collection begin/end, enumeration, request tracking, policies, error signaling, and commit.

Important design contract:
- The header documents two-phase commit requirements for device `put_params`: validate/signals first, call superclass/default handler, then install or roll back state.

Also declares:
- Typed read/write helpers.
- Table-driven item transfer API.
- `gs_c_param_list`, the concrete C parameter-list implementation with optional forwarding target.
