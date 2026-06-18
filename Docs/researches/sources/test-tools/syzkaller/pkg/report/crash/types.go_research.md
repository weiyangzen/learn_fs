# sources/test-tools/syzkaller/pkg/report/crash/types.go

Purpose: Defines normalized crash type constants, title classification, string rendering, and grouping predicates.

Important APIs and types: `Type` is a string alias. Constants include unknown, sanitizer categories, lockdep/atomic sleep, DoS, hang, leak, warning/bug families, no output, reboot, and syzkaller failure. `TitleToType` maps a title through `titleToType`. `String` renders unknown as `UNKNOWN`. Predicate methods include `IsKASAN`, `IsUAF`, `IsKMSAN`, `IsKCSAN`, `IsUBSAN`, `IsBUG`, `IsWarning`, `IsBugOrWarning`, `IsMemSafety`, `IsMemoryLeak`, `IsLockingBug`, `IsDoS`, `IsHang`, `IsLockdep`, and `IsAtomicSleep`.

Control flow and state: `TitleToType` loops definitions in order and returns on first `strings.HasPrefix`. Predicates use exact comparisons or small `slices.Contains` lists.

Dependencies and integration: Consumed by report classification, impact scoring, dashboards, triage, and analytics.

Risks: `IsUAF` currently only covers KASAN UAF types, not KFENCE/KMSAN UAF reads/writes. `IsDoS` includes `Bug` and `DoS`, which is a policy choice that callers must understand. Adding new constants requires updating predicates.

Test signals: Prefix-table structure is tested in `title_to_type_test.go`; predicate methods do not have direct tests here.
