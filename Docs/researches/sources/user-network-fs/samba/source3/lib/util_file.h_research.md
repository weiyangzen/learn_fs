<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.h -->
# sources/user-network-fs/samba/source3/lib/util_file.h

## Purpose
This header declares the async process-output loading helper.

## Important APIs, types, and functions
It exposes `file_ploadv_send` and `file_ploadv_recv`. The send function takes an argv vector and max output size. The recv function returns an error code and moves a `uint8_t *` buffer to the caller.

## Control flow
Callers start the request on a tevent context, wait for completion, and call recv once.

## State and persistence behavior
The header carries no state. Runtime state belongs to the request implementation.

## Dependencies and integration points
It includes `replace.h` and `<tevent.h>` so consumers can compile against `struct tevent_req`.

## Risks and edge cases
Callers must treat nonzero recv return as an errno-style failure and should respect max-size limits for untrusted commands.

## Test signals
Compile coverage plus behavioral tests in `util_file.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_file.h -->
