# sources/security-integrity/selinux/libselinux/include/selinux/context.h

## Purpose
`context.h` declares a small userspace API for parsing, inspecting, modifying, serializing, and freeing SELinux security contexts.

## Important APIs, types, and functions
`context_s_t` wraps an opaque `void *ptr`, and `context_t` is a pointer to that wrapper. `context_new()` parses a context string. `context_str()` returns an internal string valid until the next serialization/free on the same context. `context_to_str()` returns a caller-owned string. `context_free()` releases storage. Component getters and setters expose `user`, `role`, `type`, and `range` fields.

## Control flow
Typical use creates a context with `context_new()`, reads or updates components with getters/setters, serializes with `context_str()` or `context_to_str()`, and then calls `context_free()`.

## State and persistence behavior
State is heap-backed and process-local. Getter string pointers are borrowed from the context object, while `context_to_str()` returns independent storage that callers free with `free(3)`. The API has no direct persistence behavior.

## Dependencies and integration points
The header is C/C++ compatible and integrates with higher-level libselinux APIs that accept or return context strings. It intentionally hides the parsed representation behind an opaque pointer.

## Risks and edge cases
Borrowed pointers from getters and `context_str()` become invalid after later serialization changes or `context_free()`. Setter failures return nonzero but do not document partial mutation semantics here. Callers must distinguish `free()` for `context_to_str()` from `context_free()` for the context object.

## Test signals
Tests should parse valid and invalid contexts, mutate each component, verify serialization, check MLS range preservation, assert borrowed-pointer lifetime assumptions, and run leak/error tests for setter failures.
