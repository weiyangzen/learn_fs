# sources/user-network-fs/samba/source4/libcli/rap/rap.h

Purpose: RAP client internal header with status-handling macros, the `rap_call` structure, RAP NDR flags, generated RAP type inclusion, and generated prototypes.

Important content: macros `RAP_GOTO`, `RAP_RETURN`, `NDR_GOTO`, and `NDR_RETURN` standardize NTSTATUS/NDR error propagation. `struct rap_call` stores call number, parameter/data/aux descriptor strings, expected receive sizes, push contexts, pull memory context, and response pull contexts. `RAPNDR_FLAGS` sets no-align, ASCII, null-terminated string behavior.

Control flow contract: RAP wrappers create a `rap_call`, push descriptors and data, execute the call, then pull response data through the stored pull contexts.

State and persistence: per-call volatile state only. Remote administrative operations performed by callers may persist on the server.

Dependencies and integration: includes generated `rap.h` and `libcli/rap/proto.h`. The flags must match RAP wire format expectations.

Risks: macro `goto done` patterns require each caller to define `result` and `done` consistently. Descriptor strings and expected lengths are central to safe parsing. Test signals are compile coverage and representative wrapper calls for each macro path.
