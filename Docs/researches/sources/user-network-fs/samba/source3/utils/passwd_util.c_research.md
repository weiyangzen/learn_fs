<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_util.c -->
# sources/user-network-fs/samba/source3/utils/passwd_util.c

## Purpose

`passwd_util.c` provides the shared password-reading helper used by passdb editing tools. It supports interactive terminal prompting and script-friendly stdin input.

## Important APIs, Types, and Functions

`stdin_new_passwd()` reads one line from stdin into a static `fstring`, strips a trailing newline, and returns the static buffer. `get_pass()` selects stdin or `samba_getpass()`, then returns an `smb_xstrdup()` copy of the password.

## Control Flow

Callers pass a prompt and `stdin_get`. In stdin mode the helper reads exactly one newline-terminated password line. In interactive mode it calls `samba_getpass(prompt, pwd, sizeof(pwd), false, false)`. On read failure it returns `NULL`; otherwise it duplicates the captured password and returns ownership to the caller.

## State and Persistence Behavior

The stdin helper uses a static buffer and clears it before each read. The interactive path uses a local stack buffer. Both paths duplicate the password to heap memory; scrubbing that returned copy is the caller's responsibility. No persistent account state is changed here.

## Dependencies and Integration Points

It includes `passwd_proto.h` and relies on Samba `fstring`, `ZERO_ARRAY`, `samba_getpass()`, and `smb_xstrdup()`. `pdbedit.c` uses it while adding users and comparing repeated password entries.

## Risks and Edge Cases

The stdin path truncates input to the `fstring` size and accepts a line without a trailing newline. Because returned memory is a normal duplicate, callers must explicitly zero it. The helper does not enforce password policy; policy is applied later by account-management functions.

## Test Signals

Tests should cover stdin EOF, long stdin lines, interactive getpass failure, password strings with and without trailing newline, and caller cleanup paths that wipe both password copies after mismatch or success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/passwd_util.c -->
