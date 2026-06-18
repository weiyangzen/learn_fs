# File Research: sources/os/bsd/freebsd-src/sys/sys/rctl.h

Read completely: 171 lines.

## Purpose
Defines FreeBSD resource-control rule structures, subject/action constants, kernel enforcement APIs, and userland `rctl_*` syscall interfaces.

## Main Elements
- Describes rule linking through RACCT containers rather than a global rule list.
- Defines immutable-after-link `struct rctl_rule` with subject union, per/resource/action/amount fields, refcount, and delayed task.
- Defines subject types for process, user, loginclass, and jail.
- Maps signal actions to signal numbers and defines non-signal actions `DENY`, `LOG`, `DEVCTL`, and `THROTTLE`.
- Declares kernel APIs for rule allocation/duplication/refcounting, add/remove, enforcement, throttle decay, percent-CPU availability, effective limits/availability, resource names, credential change, fork, and RACCT release.
- Declares userland syscalls for querying RACCT usage, rules, limits, adding rules, and removing rules via input/output buffers.

## Dependencies And Integration
Tied to RACCT, process/user/loginclass/jail subjects, signal delivery, taskqueue-delayed rule freeing, and the rctl syscall ABI.

## Risk Notes
Rules are immutable after linking and refcounted through rule links. Subject/action/resource constants are ABI/KPI; malformed changes can break enforcement or userland rule parsers.
