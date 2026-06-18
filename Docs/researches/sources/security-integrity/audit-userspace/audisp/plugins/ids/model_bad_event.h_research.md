# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.h

Purpose: declares the bad-event IDS model entry point for complete auparse events.

Important APIs and data: exposes `process_bad_event_model(auparse_state_t *, struct ids_conf *)`.

Control flow: no implementation; callers pass one complete auparse event plus current config.

State and persistence: no state in the header; implementation mutates session/origin state.

Dependencies and integration: includes `auparse.h` and `ids_config.h`, coupling consumers to auparse and the IDS config structure.

Risks: the API assumes auparse state is positioned safely by the implementation; callers should not pass partial events.

Test signals: compile-time inclusion and model dispatch tests through the IDS main event loop.
