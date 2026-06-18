# sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.h

Purpose: declares delayed timer services for IDS reactions.

Important APIs and data: defines `jobs_t` enum values `UNLOCK_ACCOUNT` and `UNBLOCK_ADDRESS`; declares init, tick, add, and shutdown functions.

Control flow: no implementation; caller must invoke `do_timer_services` periodically.

State and persistence: describes in-memory timer queue behavior only.

Dependencies and integration: used by timed reaction functions and `nvpair.h`.

Risks: adding a new timed reaction requires updating the enum and the switch in `do_timer_services`.

Test signals: compile-time enum consumers and timed reaction integration.
