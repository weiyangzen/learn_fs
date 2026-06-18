<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_proto.h -->
# sources/user-network-fs/samba/source3/utils/passwd_proto.h

## Purpose

`passwd_proto.h` is the collected prototype header for password prompting helpers used by Samba account-management utilities.

## Important APIs, Types, and Functions

It declares `char *get_pass(const char *prompt, bool stdin_get)`, implemented in `passwd_util.c`. The function returns a newly allocated password string read either from stdin or from the terminal prompt.

## Control Flow

This header has no runtime flow. It allows tools such as `pdbedit.c` to call the shared password input helper.

## State and Persistence Behavior

The declared function returns heap memory that callers own and should wipe before freeing when holding secrets. The stdin path in the implementation uses a static `fstring`, but callers receive an allocated duplicate.

## Dependencies and Integration Points

It depends on Samba's common boolean type and memory helpers through the including translation unit. The principal integration point is `pdbedit` user creation with `--password-from-stdin`.

## Risks and Edge Cases

The API does not encode whether the returned secret has been zeroed or whether the caller must zero it. Callers that forget to scrub the returned buffer leave password material in process memory.

## Test Signals

Compile coverage through `pdbedit.c` validates the prototype. Functional checks should cover terminal prompt mode, stdin mode, EOF on stdin, and caller-side password mismatch handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_proto.h -->
