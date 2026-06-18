# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.h

Purpose: declares the behavior model entry point for complete auparse events.

Important APIs and data: exposes `process_behavior_model(auparse_state_t *, struct ids_conf *)`.

Control flow: none in the header; implementation dispatches by audit record type and key.

State and persistence: no header-owned state; the implementation mutates current sessions and origins.

Dependencies and integration: includes auparse and IDS config types, used by the IDS main dispatcher to chain models.

Risks: callers must provide a complete event and a valid config pointer.

Test signals: compile coverage and integration tests through model dispatch.
