# sources/test-tools/syzkaller/pkg/subsystem/linux/rules.go

## Purpose

`rules.go` contains Linux-specific policy overrides layered on top of MAINTAINERS-derived data. These rules fill gaps where path metadata alone cannot produce useful syzkaller subsystem behavior.

## Important APIs, Types, and Functions

`customRules` groups six rule maps: `subsystemCalls`, `notSubsystemEmails`, `extraSubsystems`, `noReminders`, `noIndirectCc`, and `addParents`. `linuxSubsystemRules` is the production rule set used by `ListFromRepo`.

## Control Flow

The rules are consumed by `listFromRepoInner` and `linuxCtx.applyExtraRules`. `extraSubsystems` forces named subsystems from specific MAINTAINERS records before list-based grouping. `notSubsystemEmails` excludes broad or misleading mailing lists from subsystem creation. `subsystemCalls` attaches syscall/reproducer hints used by `rawExtractor.FromProg`. `noReminders` and `noIndirectCc` alter reporting and inherited CC behavior. `addParents` adds manual parent links after inferred hierarchy generation and then transitive reduction cleans redundant edges.

## State, Dependencies, Risks, and Test Signals

The file is static data plus the `customRules` type. It has no I/O and no runtime mutation by itself. Its only direct dependency is package-local integration in `subsystems.go`. Risks are staleness as Linux MAINTAINERS and syzkaller syscall names change, dangling rule keys rejected by `noDanglingRules`, inconsistent naming exceptions, and policy choices that intentionally hide broad lists or reports. `subsystems_test.go` verifies a small custom-rules instance for syscall attachment, extra subsystem extraction, and manual parent behavior; production map coverage depends on broader list-generation tests.
