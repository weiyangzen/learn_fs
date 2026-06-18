# sources/security-integrity/selinux/libselinux/src/label_internal.h

Purpose: Defines the internal label-backend interface and shared data structures used by `label.c` and backend implementations.

Important APIs/types/functions: declares backend init functions, `struct selabel_digest`, `struct selabel_lookup_rec`, and `struct selabel_handle` with function pointers for lookup, close, stats, partial match, digest operations, best match, and compare. Declares `selabel_validate()`, `compat_validate()`, `read_spec_entries()`, and digest helpers.

Control flow: no implementation except `COMPAT_LOG` macro, which routes legacy compatibility output to `myprintf` when enabled or to `selinux_log()`.

State and persistence: describes per-handle persistent state: backend ID, validation flag, backend data pointer, spec file path, and optional digest.

Dependencies and integration: all label backends include this header to satisfy the frontend contract.

Risks and test signals: function-pointer optionality drives public API fallbacks. Tests should cover backends missing optional operations and digest structures with multiple spec files.
