# sources/security-integrity/selinux/libsepol/include/sepol/handle.h

Purpose: Declares the opaque libsepol handle API used for diagnostics and option flags.

Important APIs and functions: `sepol_handle_create/destroy`, dontaudit getters/setters, `sepol_set_expand_consume_base`, and preserve-tunables getters/setters.

Control flow: Callers create a handle, configure policy transformation options, pass it into operations, and destroy it after use.

State and persistence: The handle stores per-operation options and message callback metadata. It does not persist policy data by itself.

Dependencies and integration points: Used by nearly every public API that can report errors or honor policy expansion flags.

Risks: Null handles are accepted in many internal paths but lose user diagnostics. Option semantics affect module expansion output and must be set before operations that consume them.

Test signals: Handle lifecycle, callback behavior, dontaudit/preserve-tunable option effects, and consume-base expansion behavior validate this API.
