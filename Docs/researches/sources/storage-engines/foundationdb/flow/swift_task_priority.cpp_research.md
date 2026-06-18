# sources/storage-engines/foundationdb/flow/swift_task_priority.cpp

## Purpose
This C++ file maps Swift concurrency job-priority numeric values into FoundationDB Flow `TaskPriority` values. It is glue for scheduling Swift-originated jobs with the same relative priority ordering as Net2/Flow tasks.

## Important APIs, Types, And Functions
The central function is `TaskPriority swift_priority_to_net2(swift::JobPriority p)`. It switches on the underlying integer value of `swift::JobPriority` and returns corresponding Flow priorities such as `Max`, `RunLoop`, `ASIOReactor`, socket priorities, coordination priorities, cluster-controller priorities, proxy/TLog priorities, default/yield/delay priorities, disk IO priorities, data-distribution priorities, restore priorities, `Low`, `Min`, and `Zero`.

## Control Flow
The function casts the Swift priority enum to its underlying type, enters a large switch, assigns a `TaskPriority`, and returns it. Unknown priorities print the raw value and abort. Priority value `12` is explicitly marked deleted and asserts false. The mapping is manually maintained and mirrors Flow's priority ladder.

## State And Persistence
There is no persistent state. The function is a pure mapping for recognized values except for abort/assert side effects on invalid inputs and optional diagnostic printing on unknown priorities.

## Dependencies And Integration Points
The file includes `flow/swift.h`, `flow/swift_concurrency_hooks.h`, Swift ABI `Task.h`, and `TLSConfig.h`. Its intended integration point is the Swift enqueue hook or any scheduler bridge that needs to convert Swift job priority into Net2 ordered-task priority.

## Risks
The mapping is manually synchronized with Swift-side or generated priority values; any addition, deletion, or renumbering can silently misprioritize work or abort at runtime. The current enqueue hook in `swift_concurrency_hooks.cpp` has the mapping code commented out, so this function may be underused and drift. Aborting on unknown priority is appropriate for invariant enforcement but risky if Swift runtime values change independently. The deleted priority case only asserts, which may behave differently in release builds depending on `ASSERT` configuration.

## Test Signals
Tests should enumerate all known Swift priority values and verify exact `TaskPriority` outputs, including boundary values 0, 1, 255 and deleted/unknown handling. Build-time generation or static assertions comparing Flow and Swift priority tables would be a stronger signal than hand-maintained switch coverage.
