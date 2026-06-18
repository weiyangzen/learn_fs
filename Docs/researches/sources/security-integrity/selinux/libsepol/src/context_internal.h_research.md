# sources/security-integrity/selinux/libsepol/src/context_internal.h

Purpose: Provides the internal include bridge for context public APIs.

Important APIs and types: It declares no new symbols; it includes `sepol/context.h` and `sepol/context_record.h`.

Control flow: No logic exists. Implementation files include it to access public context declarations consistently.

State and persistence: No state.

Dependencies and integration points: Used by `context.c`, `context_record.c`, and internal headers.

Risks: Low; as a wrapper, it can mask direct dependency changes in public context headers.

Test signals: Context implementation compilation validates it.
