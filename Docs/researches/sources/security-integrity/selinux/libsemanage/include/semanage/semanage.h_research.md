# sources/security-integrity/selinux/libsemanage/include/semanage/semanage.h

Purpose: umbrella public header for libsemanage. It aggregates handle, modules, debug, record, local database, policy database, and active boolean APIs into one include.

Important APIs/types/functions: includes the handle and module APIs first, then record definitions for booleans, users, seusers, contexts, interfaces, ports, InfiniBand keys/endports, and nodes, followed by local/policy database headers and active boolean access.

Control flow: applications that include this header can compile against the whole public API without tracking per-object headers. The header itself performs no logic; ordering matters to satisfy opaque type dependencies.

State and persistence behavior: no runtime state. Its persistence impact is ABI/API exposure: anything included here is part of the broad public surface and is seen by SWIG exception generation.

Dependencies and integration points: used by examples, bindings, documentation, package consumers, and `exception.sh`, which compiles this header to discover extern integer-returning functions for Python exception wrappers.

Risks: adding a header here expands public API visibility and may affect generated bindings. Missing an object header makes the umbrella incomplete. Test signals are clean compilation of a program including only `semanage/semanage.h`, SWIG generation success, and installed-header completeness.
