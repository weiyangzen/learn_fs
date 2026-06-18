# sources/test-tools/syzkaller/pkg/subsystem/linux/subsystems.go

## Purpose

`subsystems.go` is the assembly pipeline that turns a Linux repository into syzkaller `Subsystem` objects plus debug metadata. It connects MAINTAINERS parsing, custom rules, path-rule matching, hierarchy inference, naming, sorting, and service-facing metadata.

## Important APIs, Types, and Functions

`ListFromRepo(repo string)` wraps `os.DirFS` and calls `listFromRepoInner`. `linuxCtx` stores the filesystem, raw records, and optional custom rules. Key methods are `groupByList`, `groupByRules`, and `applyExtraRules`. Helpers include `noDanglingRules`, `mergeRawRecords`, `unique`, `maintainersFromRecords`, and `getMaintainers`.

## Control Flow

The pipeline opens `MAINTAINERS`, parses records, removes documentation/scripts/samples/tools/Makefile patterns, extracts forced subsystems from `extraSubsystems`, groups remaining records by list email, builds a coincidence matrix over the repo tree, applies parent transformations, assigns unique names, applies syscall/reminder/CC/manual-parent rules, and sorts subsystems and path rules deterministically. Debug output includes parent-child comments and matched file lists.

## State, Dependencies, Risks, and Test Signals

The function mutates records and subsystem objects in memory, but does not persist files. Dependencies include `io/fs`, `os.DirFS`, regex, sorting helpers, `golang.org/x/exp/maps`, MAINTAINERS parser, coincidence builder, name assignment, and `subsystem.DebugInfo`. Risks include dangling custom rules, missing MAINTAINERS records, broad pattern drops, maintainer intersection heuristics returning no maintainers, filesystem walk errors, and generated name churn. Tests cover grouping, custom syscalls and extra subsystems, path matching, inferred and manual parents.
