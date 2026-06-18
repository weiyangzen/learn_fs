# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rctl.h

## Role

`rctl.h` defines illumos resource-control ABI flags, privilege levels, user syscalls, entity types, and the kernel’s resource-control data model and operations.

## Public ABI

It defines local actions such as no-action, signal, deny, maximal, and project-database-originated controls. Global actions/properties include syslog, nobasic, lowerable, deny behavior, file-size/CPU-time classes, no local action, infinity, unobservable, unit types, and syslog suppression.

`getrctl()` flags include first, next, and usage. `setrctl()` operations include insert, delete, replace, and recipient-PID use.

`rctl_qty_t` is the resource quantity type and `rctl_priv_t` names basic, privileged, and system values.

Entities are process, task, project, and zone.

## Kernel Model

Kernel-only structures include:
- `rctl_val_t`: one enforced value with privilege, quantity, local actions, signal recipient, and firing time.
- `rctl_ops_t`: action, usage, set, and test callbacks.
- `rctl_t`: a resource control instance with value list/cursor and dictionary entry.
- `rctl_set_t`: hash table of controls for one entity type.
- `rctl_dict_entry_t`: global resource-control metadata and callbacks.
- `rctl_alloc_gp_t`: preallocation bundle for controls and values.

## Kernel Interfaces

The header declares registration, lookup, default-limit, legacy-limit, model maximum/value, validation, enforced-value, test/action, set creation/dup/reset/free, local get/insert/delete/replace, rlimit translation, locked-memory/swap/lofi accounting, and kstat creation helpers.

## Research Notes

`rctl.h` is a central policy/enforcement header for process, task, project, and zone resource limits. The sorted value list, cursor semantics, callback operations, and preallocation paths are important for correctness under low-memory and enforcement-time constraints.
