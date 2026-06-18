# sources/security-integrity/audit-userspace/src/auditd-event.h

## Purpose
`auditd-event.h` defines the event object and event-processing API shared by daemon core, listener, reconfiguration, and tests.

## Important APIs, Types, And Functions
It defines `ack_func_type`, `struct auditd_event`, and declarations for event lifecycle, formatting, queueing, handling, distribution, logging state, shutdown, and remote event creation. `struct auditd_event` wraps `struct audit_reply` plus optional ack callback data and a remote sequence id.

## Control Flow
Headers consumers create or receive an event, optionally attach network ack information, call `format_event`, `handle_event`, `enqueue_event`, or `distribute_event`, and then rely on `cleanup_event` to free dynamic message/event storage. Network-originating events are identified by a non-null `ack_func`.

## State And Persistence
No state is stored in the header. It documents the shape of transient event state and exposes logging state writers/resume helpers backed by `auditd-event.c`.

## Dependencies And Integration
The header includes `libaudit.h`, `gcc-attributes.h`, and `auditd-config.h`, creating a mutual dependency that is managed by include guards. It is used by `auditd.c`, `auditd-listen.c`, `auditd-reconfig.c`, `auditd-reconfigure.h`, and tests.

## Risks
The public struct exposes internal ownership-sensitive fields directly. Duplicate declarations of `auditd_get_exec_pid` and `auditd_clear_exec_pid` are harmless but noisy. Any caller that sets `ack_func` changes formatting/length semantics for network-originating events.

## Test Signals
Compile and link tests around `format_event_test` validate the header contract. Unit tests should cover `create_event` / `cleanup_event` ownership combinations for network and local events.
