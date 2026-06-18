# File Research: sources/virtualization/qemu/block/throttle-groups.c

`throttle-groups.c` implements shared I/O throttling groups. Multiple `ThrottleGroupMember` instances can share one `ThrottleState`, while each member has its own AIO context, timers, pending queues, and round-robin position. It also exposes QOM `throttle-group` objects for monitor/QAPI configuration.

The private `ThrottleGroup` object contains the QOM parent, initialized flag, immutable name, a mutex protecting shared throttling state, `ThrottleState ts`, a list of members, per-direction round-robin tokens, per-direction `any_timer_armed` flags, and the clock type. All group objects are tracked in a global `throttle_groups` tail queue protected by the global QEMU mutex.

Lifetime helpers are name-based. `throttle_group_by_name()` searches the global list. `throttle_group_exists()` reports presence. `throttle_group_incref()` returns the group's `ThrottleState`, creating and completing a new `TYPE_THROTTLE_GROUP` object if absent. `throttle_group_unref()` drops the object reference. `throttle_group_get_name()` recovers the group name from a member's `ThrottleState`.

Scheduling is round-robin and per direction (`THROTTLE_READ`, `THROTTLE_WRITE`). `next_throttle_token()` advances from the current token to the next member with pending requests, with a special path for members whose `io_limits_disabled` is set during drain. `throttle_group_schedule_timer()` checks whether limits require waiting; if no group timer is armed, it calls `throttle_schedule_timer()` and records the member as the token. `schedule_next_request()` selects the next pending member, schedules a timer if needed, or immediately restarts a coroutine queue/timer.

`throttle_group_co_io_limits_intercept()` is the runtime interception point used by the throttle filter. It locks the group, decides whether the request must wait, queues the current coroutine on the member's `throttled_reqs[direction]` if a timer or prior pending request exists, accounts the bytes with `throttle_account()`, schedules the next request, and unlocks. This makes the shared `ThrottleState` enforce aggregate limits across all members while preserving fairness.

Restart machinery uses `RestartData` and a coroutine entry point. `throttle_group_restart_queue()` creates a coroutine in the member's AIO context and increments `restart_pending`. The coroutine clears `any_timer_armed` if appropriate, wakes one queued request, schedules another if the queue was empty, decrements `restart_pending`, and kicks `aio_wait`. `throttle_group_restart_tgm()` forces all directions of one member to progress, handling three cases: this member owns a pending timer, another member owns a pending timer, or no timer exists.

Configuration functions wrap the throttle library under the group mutex. `throttle_group_config()` atomically applies a `ThrottleConfig` and restarts queues. `throttle_group_get_config()` reads it. QOM property setters/getters map `x-iops-*`, `x-bps-*`, burst lengths, and `x-iops-size` into `ThrottleConfig`; individual property changes are only allowed before initialization because valid combinations require transactional validation. The `limits` property accepts/returns a full `ThrottleLimits` QAPI object.

Member registration and removal are careful around timers and AIO contexts. `throttle_group_register_tgm()` increfs/creates the group, initializes member queues, installs initial tokens if needed, inserts the member, and initializes timers with read/write callbacks. `throttle_group_unregister_tgm()` waits for pending restart coroutines, asserts no pending throttled requests or timers remain, updates tokens if removing the current token, removes the member, destroys timers, unreferences the group, and nulls the state pointer. Attach/detach functions move timers between AIO contexts and, on detach, reschedule any pending group work before destroying timer bindings.

The QOM type defaults to realtime clock, but qtest uses virtual clock for deterministic throttling tests. `complete` validates config and inserts the group into the global list; `finalize` removes initialized groups and frees resources; `can_be_deleted` allows deletion only when the object refcount is one.

Important risks and invariants:
- The group mutex protects both shared `ThrottleState` and cross-member fields; callers outside this file should not touch those internals.
- `throttle_timers` may be temporarily invalid during AIO context changes, so cross-member timer access is guarded by pending-request checks and detach assertions.
- Unregister requires the caller to drain first.
- `io_limits_disabled` is atomic because drain paths bypass normal throttling and can interact with scheduling.
