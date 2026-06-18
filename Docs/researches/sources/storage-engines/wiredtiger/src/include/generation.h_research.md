## sources/storage-engines/wiredtiger/src/include/generation.h

Purpose: this header defines callback cookie structs for WiredTiger's generation tracking logic. Generations are used to coordinate resource lifetime and determine whether sessions are still active in a generation before reclaiming or advancing shared resources.

Important APIs/types/functions: `WT_GENERATION_COOKIE` carries `ret_active`, `ret_oldest_gen`, `which`, and `target_generation` while walking sessions to ask whether a target generation is still active and what the oldest seen generation is. `WT_GENERATION_DRAIN_COOKIE` embeds the base cookie and adds `start`, `minutes`, `pause_cnt`, and `verbose_timeout_flags` for drain operations that may wait and report progress/timeouts.

Control flow: session-walk code passes these cookies to callbacks. The callback reads each session's generation for the selected resource (`which`), updates whether the target is active, and records the oldest generation. Drain control uses the extended cookie to pause, track elapsed time, and decide whether to emit verbose timeout diagnostics.

State and persistence behavior: the cookies are stack/transient control state, not persistent state. They coordinate safe reclamation of in-memory resources that may protect persistent structures indirectly, such as data handles, hazard-protected pages, metadata views, or checkpoint-related resources.

Dependencies and integration points: it depends on `struct timespec`, `uint64_t`, `bool`, and generation constants/arrays defined elsewhere in the WiredTiger connection and session structures. It integrates with `generation_inline.h` and functions declared in `extern.h` such as `__wt_gen_active`, `__wt_gen_init`, `__wt_gen_next_drain`, `__wt_session_gen_enter`, and `__wt_session_gen_leave`.

Risks: incorrect cookie updates can free resources while a session still references them or can stall drains forever. Timeout reporting fields must not change behavior in a way that hides a stuck generation. The embedded-base layout is simple but assumes callbacks know when they can treat the drain cookie as a base generation cookie.

Test signals: generation drain tests, handle sweep tests, cache/session close tests, long-running cursor plus schema operation tests, diagnostic timeout tests, and sanitizer runs that catch use-after-free are relevant.
