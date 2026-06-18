# sources/security-integrity/audit-userspace/src/libev/ev.h

Purpose: declares the public native libev API and watcher data structures for the bundled event loop. It is the contract consumed by `ev.c`, `event.c`, and any audit-userspace code using native libev watchers.

Important APIs/types: defines feature flags (`EV_FEATURE_*`), watcher enable macros, timestamp type `ev_tstamp`, multiplicity macros (`EV_P`, `EV_A`, `EV_DEFAULT`), event masks (`EV_READ`, `EV_WRITE`, `EV_TIMER`, `EV_SIGNAL`, etc.), watcher base macros, watcher structs (`ev_io`, `ev_timer`, `ev_periodic`, `ev_signal`, `ev_child`, `ev_stat`, `ev_idle`, `ev_prepare`, `ev_check`, `ev_fork`, `ev_cleanup`, `ev_embed`, `ev_async`), `union ev_any_watcher`, loop flags, backend flags, and prototypes for loop lifecycle, run control, pending/event feeding, and watcher start/stop functions.

Control flow: this header does not execute runtime control flow, but it defines the initialization macros used by callers. `ev_init` clears active/pending state and stores a callback; `ev_TYPE_set` macros assign type-specific read-only fields; `ev_TYPE_init` macros combine both. Inline helpers expose default-loop access, activity/pending checks, priorities, callback storage, and compatibility names for pre-4.0 APIs.

State and persistence: watcher structs are caller-owned and persist as long as they may be active or pending in a loop. The `active` and `pending` fields are private loop-owned indexes; `data` is user-owned by default through `EV_COMMON`. The header supports changing `EV_COMMON`, priorities, multiplicity, and feature macros at compile time, which changes structure layout and binary compatibility.

Dependencies and integration: used directly by `ev.c` and by compatibility wrappers. It includes standard headers conditionally for atomics and stat support. The ABI version is declared as 4.33. `event.c` embeds libevent-compatible fields that wrap these native watchers.

Risks: applications must not move or free active/pending watchers and must not mutate read-only fields such as fd/signum while active. Feature macros can remove watcher types or alter `struct ev_loop` handling. The callback setter uses `memmove` to avoid strict-aliasing issues, and build flags should preserve that assumption. Child and signal watchers are restricted to the default loop.

Test signals: compile consumers in C and C++ modes with representative feature combinations, verify watcher struct layout assumptions through build tests, and exercise each init/start/stop pair through `ev.c` integration tests.
