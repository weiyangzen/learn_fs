# sources/security-integrity/audit-userspace/audisp/plugins/ids/nvpair.h

Purpose: declares the IDS timer job list types and operations.

Important APIs and data: `nvnode` stores `jobs_t job`, `char *arg`, `time_t expiration`, and `next`; `nvlist` stores `head`, `cur`, `prev`, and `cnt`. Inline helpers expose first/current cursor access.

Control flow: no implementation except inline cursor assignment and getter.

State and persistence: describes in-memory linked list state only.

Dependencies and integration: includes `timer-services.h`, tying nodes to timer job enum values.

Risks: exposed mutable fields let callers break list invariants. Ownership of `arg` is not obvious from the type alone.

Test signals: compile-time users in timer services and behavioral tests for cursor mutation.
