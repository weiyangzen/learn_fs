## sources/security-integrity/audit-userspace/src/ausearch-nvpair.h

Purpose: declares the name/value list used for lookup caches.

Important APIs/types: `nvnode` stores `name`, `val`, and `next`; `nvlist` stores head/current/count. Public APIs create, append, clear, get current, and find by value.

Control flow/state: list users rely on `cur` being positioned on a found or newly appended node.

Dependencies/integration: included by lookup/parser modules; only requires system types.

Risks/test signals: no const ownership annotation for `name`, but clear frees it. Tests should catch accidental use of string literals with `search_list_append()`.
