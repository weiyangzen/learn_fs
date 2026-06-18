# sources/security-integrity/audit-userspace/src/auditd-dispatch.h

## Purpose
`auditd-dispatch.h` declares auditd's dispatcher facade. It hides libdisp details from the rest of auditd and exposes only lifecycle and event-queue operations.

## Important APIs, Types, And Functions
The API is `init_dispatcher`, `shutdown_dispatcher`, `reconfigure_dispatcher`, and `dispatch_event`. The header imports `auditd-config.h` so lifecycle calls can consume `struct daemon_conf`; `dispatch_event` uses `struct audit_reply` through included audit headers.

## Control Flow
Consumers initialize after event/log setup, call `dispatch_event` as part of normal event distribution, reconfigure after live config changes, and shut down during daemon exit. The header itself has no code paths.

## State And Persistence
No state is defined here. It formalizes the expectation that dispatcher state is managed behind the declared functions.

## Dependencies And Integration
It integrates with `auditd.c` and `auditd-reconfigure.c`. It also couples the daemon to libdisp's protocol constants through `auditd-dispatch.c`.

## Risks
Because return values distinguish success, queue overflow/suspension, and other errors in the implementation, callers need to preserve that semantic if they begin handling dispatch failures more explicitly. The header does not document ownership of queued event memory, so implementation knowledge is required.

## Test Signals
Build tests confirm the header is usable by daemon and reconfigure modules. API tests should validate that all callers include this header rather than depending directly on libdisp.
