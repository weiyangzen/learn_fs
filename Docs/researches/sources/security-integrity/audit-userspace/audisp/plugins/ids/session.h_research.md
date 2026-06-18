# sources/security-integrity/audit-userspace/audisp/plugins/ids/session.h

Purpose: declares session tracking data and APIs.

Important APIs and data: `session_data_t` embeds `avl_t` first, then `session`, `score`, `killed`, `origin`, and `acct`. Functions expose lifecycle, lookup, current pointer, deletion, traversal, and score changes.

Control flow: no implementation in header.

State and persistence: describes process-local session state only.

Dependencies and integration: includes `avl.h`, `origin.h`, and `ids_config.h`; used by models and reactions.

Risks: public fields can be mutated without maintaining AVL/current invariants. `origin` is IPv4-only by design.

Test signals: compile-time inclusion and integration tests around session lifecycle.
