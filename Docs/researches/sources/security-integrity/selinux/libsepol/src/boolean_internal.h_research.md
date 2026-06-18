# sources/security-integrity/selinux/libsepol/src/boolean_internal.h

Purpose: Provides the internal include bridge for boolean record and collection APIs.

Important APIs and types: It does not declare new symbols; it includes `sepol/boolean_record.h` and `sepol/booleans.h`.

Control flow: No logic exists. Implementation files include this header to share public boolean type declarations internally.

State and persistence: No state.

Dependencies and integration points: Used by `boolean_record.c` and potentially boolean-related internals.

Risks: As a thin wrapper, risk is low. It can hide direct dependency needs if public headers change.

Test signals: Boolean implementation compilation validates it.
