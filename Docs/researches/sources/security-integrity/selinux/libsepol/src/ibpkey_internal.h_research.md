# sources/security-integrity/selinux/libsepol/src/ibpkey_internal.h

Purpose: private include shim for InfiniBand partition-key record and collection APIs.

Important APIs and types: includes `<sepol/ibpkey_record.h>` and `<sepol/ibpkeys.h>` under an include guard. It declares no additional implementation detail.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `ibpkey_record.c` and `ibpkeys.c` to share public pkey declarations through a local internal header.

Risks: minimal compile-time include coupling only.

Test signals: compile pkey record and policydb adapter modules with public headers.
