# sources/security-integrity/selinux/libsepol/src/ibendport_internal.h

Purpose: private include shim for InfiniBand end-port record and collection APIs.

Important APIs and types: it includes `<sepol/ibendport_record.h>` and `<sepol/ibendports.h>` under an internal include guard; no new types or functions are declared here.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `ibendport_record.c` and `ibendports.c` so those modules can share the public record/collection declarations through a local internal header.

Risks: minimal; it mainly centralizes includes. Header drift would affect compilation of end-port modules.

Test signals: compile the InfiniBand end-port record and policydb adapter modules against public headers.
