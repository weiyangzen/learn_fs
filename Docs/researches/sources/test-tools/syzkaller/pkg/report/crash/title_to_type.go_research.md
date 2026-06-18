# sources/test-tools/syzkaller/pkg/report/crash/title_to_type.go

Purpose: Defines ordered mappings from syzkaller crash title prefixes to normalized crash `Type` values.

Important data: `titleToType` is an ordered slice of include-prefix groups. It maps KFENCE, KMSAN, KASAN, null pointer, memory-safety, KCSAN, lockdep, atomic-sleep, leak, BUG/WARNING, hang, DoS, no-output, reboot, and syzkaller failure prefixes to crash types, followed by broad defaults for `WARNING:`, `BUG:`, `INFO:`, sanitizer families, and UBSAN.

Control flow and state: This file is data-only. Runtime lookup is implemented by `TitleToType` in `types.go`, which returns the first prefix match. Ordering is therefore semantically important: more specific prefixes must precede broader prefixes.

Dependencies and integration: Used by report impact scoring, dashboards, analytics, and any logic grouping crashes by class.

Risks: Prefix overlap can shadow later mappings. Broad defaults intentionally classify unknown sanitizer titles but can hide the need for more specific types. Comments mention keep-sorted regions, but global ordering is priority-driven rather than purely alphabetical.

Test signals: `title_to_type_test.go` validates non-empty prefixes, duplicate prevention, and that no prefix is already matched by an earlier prefix.
