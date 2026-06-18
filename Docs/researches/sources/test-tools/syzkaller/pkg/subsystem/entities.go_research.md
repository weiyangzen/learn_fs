# sources/test-tools/syzkaller/pkg/subsystem/entities.go

## Purpose

`entities.go` defines subsystem metadata used for ownership, mailing-list routing, path matching, and debugging.

## Important APIs, Types, And Control Flow

`Subsystem` stores name, path rules, syscall names, mailing lists, maintainers, parent subsystems, and flags controlling reminders and indirect CC. `ReachableParents` recursively walks parent links, panicking on a direct/recursive return to the starting subsystem. `Emails` returns this subsystem's lists and maintainers plus parent lists unless `NoIndirectCc` is set. `FilterList` applies a predicate to a subsystem list, mutates each kept subsystem's `Parents` to only kept parents, and returns kept items. `PathRule.IsEmpty` checks include/exclude regex strings. `DebugInfo` stores parent-child comments and file lists.

## State, Dependencies, Integration, Risks, And Test Signals

The file has no external dependencies. State is caller-owned graph data, and `FilterList` mutates it in place. Integration points include subsystem matching, report CC generation, and syzbot dashboard/reporting logic. Risks include cycles not involving the starting node causing unbounded recursion, map iteration nondeterminism in parent email ordering, duplicate emails, and surprising parent mutation during filtering. No direct tests are in this subset; callers should test cycle handling, filtering side effects, and email ordering/dedup expectations.
