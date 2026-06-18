# sources/security-integrity/selinux/libsemanage/src/context_record.c

Purpose: implements public semanage context helpers as wrappers around libsepol security-context records.

Important APIs/types/functions: exports getters/setters for user, role, type, MLS range, create/clone/free, `semanage_context_from_string`, and `semanage_context_to_string`.

Control flow: field operations delegate to `sepol_context_*` with `handle->sepolh`. String parsing creates a context from a SELinux context string; serialization returns an allocated string for the caller.

State and persistence behavior: contexts are heap objects embedded in higher-level records such as file contexts, ports, nodes, interfaces, and InfiniBand records. They are persisted only when their owning record is written to a backend.

Dependencies and integration points: depends on libsepol context APIs and semanage handles. It is a shared building block across most context-bearing record types.

Risks: getter pointers are borrowed; setters can fail on allocation or invalid components. Test signals include string round trips, clone independence, MLS handling, and cleanup of nested contexts in owning records.
