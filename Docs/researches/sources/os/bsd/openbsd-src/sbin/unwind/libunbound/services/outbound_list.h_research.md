# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/outbound_list.h

## Role

Declares the outbound serviced-query tracking list used by module-specific query state.

## Main Types

- `struct outbound_list`: owner-side list head containing `first`.
- `struct outbound_entry`: doubly linked entry containing `next`, `prev`, the sent `serviced_query`, and the originating `module_qstate`.

## Public API

- `outbound_list_init`: initialize caller-owned list storage.
- `outbound_list_clear`: stop and remove all serviced queries in the list.
- `outbound_list_insert`: insert a caller-allocated entry.
- `outbound_list_remove`: stop and unlink one entry.

## Research Notes

- The header says callers allocate entries; the C implementation assumes they are usually tied to a broader region/lifetime and are not individually freed on removal.
- This list is part of per-module qstate bookkeeping, not a global outbound scheduler.
