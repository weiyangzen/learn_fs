# sources/security-integrity/selinux/libselinux/src/context_internal.h

Purpose: Internal include shim for the public SELinux context API.

Important APIs/types/functions: it includes `<selinux/context.h>` and introduces no additional declarations.

Control flow: none.

State and persistence: none.

Dependencies and integration: gives internal source files a local include path for `context_t` and context component APIs.

Risks and test signals: minimal risk; compile coverage verifies the include path and public header availability.
