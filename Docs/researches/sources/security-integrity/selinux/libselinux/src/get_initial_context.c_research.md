# sources/security-integrity/selinux/libselinux/src/get_initial_context.c

Purpose: Reads named initial security contexts from `selinuxfs/initial_contexts`.

Important APIs/types/functions: `security_get_initial_context_raw()` reads a raw context for a name. `security_get_initial_context()` translates the returned raw context.

Control flow: raw function rejects names containing `/`, builds `selinux_mnt/initial_contexts/<name>` with overflow checks, opens read-only, reads up to one page, duplicates the buffer, and returns it.

State and persistence: read-only kernel policy state.

Dependencies and integration: used by `avc_get_initial_sid()` and callers needing kernel initial SIDs.

Risks and test signals: path traversal prevention is important. Tests should cover slash rejection, long names, missing initial context, empty reads, and translation failure.
