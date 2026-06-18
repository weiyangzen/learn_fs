# sources/user-network-fs/samba/source4/librpc/ndr/py_security.c

## Purpose

`py_security.c` patches generated Python bindings for security-related NDR types and the security module. It adds SID usability, security descriptor ACL mutation and SDDL conversion, token helper methods, module privilege helpers, random SID generation, and ACE comparison/SDDL conversion.

## Important APIs And Types

`PyType_AddMethods()` injects methods into generated type dictionaries. `dom_sid` additions include constructor from string, `str`, `repr`, rich comparison via `dom_sid_compare()`, and `.split()` returning domain SID plus RID.

`security_descriptor` additions include a custom `tp_new` using `security_descriptor_initialise(NULL)`, rich equality via `security_descriptor_equal()`, SACL/DACL add/delete helpers, ACE-specific delete helpers, class method `from_sddl()`, and instance method `as_sddl()`. `from_sddl()` supports keyword-only `allow_device_in_sddl` and raises module-specific `security.SDDLValueError` with parse details.

`security_token` additions include a custom constructor with optional `evaluate_claims`, SID membership checks, anonymous/system/admin/authenticated-users checks, privilege checks, and privilege mutation. Module methods include `random_sid`, `privilege_id`, and `privilege_name`. `security_ace` additions include equality and `as_sddl()`.

## Control Flow And State

Most functions are immediate Python method calls mutating in-memory C structures. Descriptor ACL insert/delete helpers call libcli security routines and raise Python errors on NTSTATUS failure. SDDL decode allocates under a temporary talloc context, steals the decoded descriptor to a stable context, and wraps it as a Python object. `py_mod_security_patch()` adds module functions and creates the `SDDLValueError` exception during module initialization.

## Dependencies And Integration Points

The file depends on Python C API, generated conditional ACE support, py3 compatibility, SDDL encode/decode, and libcli security primitives. It is a major integration layer for Samba Python code that manipulates ACLs, SIDs, tokens, privileges, and SDDL strings.

## Risks

Security descriptor mutation is access-control-sensitive; type checks and NTSTATUS propagation must remain strict. `from_sddl()` intentionally includes the original SDDL string in the exception tuple, which is useful for diagnostics but can expose sensitive ACL text to logs if callers print exceptions. `random_sid()` uses `generate_random()` to produce three RID authority components; it is for test/utility use, not a domain SID authority source. `as_sddl()` and ACE encoding require a domain SID argument in some paths and should reject wrong types.

## Test Signals

Python tests should cover SID parse/format/split/compare, descriptor creation, DACL/SACL add/delete by SID and ACE, SDDL round trips including invalid SDDL exception tuple fields, token SID/privilege helper methods, privilege name/id invalid values, random SID format, and ACE equality/SDDL encoding.
