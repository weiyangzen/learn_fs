# sources/security-integrity/audit-userspace/src/auditd-reconfigure.h

## Purpose
`auditd-reconfigure.h` defines the context boundary used to apply a live configuration update without hard-linking all logging internals into the reconfigure implementation.

## Important APIs, Types, And Functions
It defines `struct auditd_reconfigure_state` for pointers to mutable logging flags and `FILE *`, `struct auditd_reconfigure_ops` for callbacks back into the event/logging layer, `struct auditd_reconfigure_context` for event/config/state/ops plus change flags, and `auditd_reconfigure`.

## Control Flow
`auditd-event.c` constructs the context, filling pointers and callbacks, then calls `auditd_reconfigure`. The applier toggles `need_size_check`, `need_reopen`, and `need_space_check` while mutating config and invoking callbacks.

## State And Persistence
The header describes borrowed pointers into `auditd-event.c` state rather than owning state itself. It enables reconfigure code to close/reopen persistent log files and reset warning flags through controlled indirection.

## Dependencies And Integration
It includes `<stdio.h>` and `auditd-event.h`, which brings in `struct daemon_conf`. It is included by `auditd-event.c` and `auditd-reconfigure.c`.

## Risks
Callback pointers are trusted and not null-checked by the implementation. Because the state fields are raw pointers, incorrect context construction could corrupt daemon logging state. The context is synchronous, so callers must not outlive borrowed event/config pointers.

## Test Signals
Compile coverage exists via `format_event_test`. Unit tests should build mock contexts with instrumented callbacks to verify call ordering and guard against null or invalid callback regressions if the API expands.
