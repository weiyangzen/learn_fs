# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd_private.h

## Purpose
This private header defines notifyd's internal database record layout and the parser prototype shared by implementation files.

## Important APIs, Types, and Functions
`struct notifyd_watcher` stores aggregate direct and recursive filters, the remaining filters that the system watcher could not handle, and the backend watch handle. `struct notifyd_instance` stores one client `server_id` plus the public `notify_instance`. `notifyd_parse_entry()` is declared for parsing raw db values.

## Control Flow
The types are used whenever notifyd reads, writes, marshals, or traverses the entries db. `notifyd_apply_rec_change()` recalculates watcher filters from instances and stores these structs contiguously; trigger dispatch parses them to decide which clients to notify.

## State and Persistence
The structs are stored verbatim in the in-memory db. `sys_watch` is a live process pointer, not durable data. `sys_filter` and `sys_subdir_filter` are in/out masks handed to the backend so notifyd can distinguish events already covered by system notify from those that need explicit smbd trigger handling.

## Dependencies and Integration Points
It includes Samba replacement and server-id utilities plus `notifyd.h`. It is intentionally private to the notifyd subsystem and should not be treated as a stable external ABI.

## Risks and Edge Cases
The comment says watcher filters are an "intersections" of filters, but the implementation ORs filters together. Future changes should preserve the actual aggregate-union behavior unless deliberately redesigning watcher registration. Because these structs are raw db storage, padding and pointer fields must be considered when marshaling or comparing records.

## Test Signals
Coverage is indirect through all notifyd tests. Structural changes should be accompanied by parser tests and add/update/delete tests that verify aggregate filter recalculation.
