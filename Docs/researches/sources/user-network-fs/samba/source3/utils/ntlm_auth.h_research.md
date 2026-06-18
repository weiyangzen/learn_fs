<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.h -->
# sources/user-network-fs/samba/source3/utils/ntlm_auth.h

## Purpose

`ntlm_auth.h` is the small public coordination header for the NTLM authentication utility. It includes the collected prototype header and exposes command option globals needed by the diagnostics translation unit.

## Important APIs, Types, and Functions

The header includes `utils/ntlm_auth_proto.h` and declares `extern const char *opt_username`, `opt_domain`, `opt_workstation`, and `opt_password`. These globals are defined in `ntlm_auth.c` and consumed by `ntlm_auth_diagnostics.c`.

## Control Flow

There is no runtime control flow in this header. Its compile-time role is to make the main utility's parsed option state visible to diagnostics helpers and to surface the helper function prototypes.

## State and Persistence Behavior

The declared globals carry process-wide authentication identity and password state. Because diagnostics reads them directly, diagnostics must be run after `main()` has parsed defaults and prompted or accepted a password. The state is not isolated per test.

## Dependencies and Integration Points

This header couples `ntlm_auth.c`, `ntlm_auth_diagnostics.c`, and `ntlm_auth_proto.h`. It also inherits all type requirements for `DATA_BLOB`, `NTSTATUS`, and `TALLOC_CTX` through included Samba headers.

## Risks and Edge Cases

The diagnostics code depends on mutable process-global option state rather than a parameter object. Any future attempt to run diagnostics independently, reentrantly, or in parallel would need to break this coupling. Since `opt_password` is an extern pointer, callers must also preserve its lifetime for the whole diagnostic pass.

## Test Signals

Compile coverage should ensure both `ntlm_auth.c` and `ntlm_auth_diagnostics.c` include this header cleanly. Behavioral coverage comes from running `ntlm_auth --diagnostics`, which proves the extern option handoff is initialized before diagnostics reads it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/ntlm_auth.h -->
