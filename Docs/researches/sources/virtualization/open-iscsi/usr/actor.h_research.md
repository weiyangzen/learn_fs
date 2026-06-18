# File Research: sources/virtualization/open-iscsi/usr/actor.h

Declares the actor scheduler API and the `actor_t` structure. An actor has a debug name, list linkage, state, opaque data, callback, and scheduled time.

Key definitions:
- `ACTOR_INVALID`, `ACTOR_WAITING`, `ACTOR_SCHEDULED`, `ACTOR_NOTSCHEDULED`.
- `ACTOR_NAME_LEN` is 128.
- Public functions cover init, delete, immediate scheduling, timer scheduling/modification, and polling.
- `actor_init` and `actor_timer` macros fill `name` with the callback symbol string before calling internal setup functions.

This header couples the scheduler to the project `list.h` intrusive list implementation and `types.h`.
