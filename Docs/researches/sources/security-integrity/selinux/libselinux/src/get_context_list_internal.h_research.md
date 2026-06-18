# sources/security-integrity/selinux/libselinux/src/get_context_list_internal.h

Purpose: Internal include shim for public get-context-list declarations.

Important APIs/types/functions: includes `<selinux/get_context_list.h>` with no extra declarations.

Control flow: none.

State and persistence: none.

Dependencies and integration: used by `get_context_list.c` to reference public prototypes while keeping local include style.

Risks and test signals: compile coverage is sufficient.
