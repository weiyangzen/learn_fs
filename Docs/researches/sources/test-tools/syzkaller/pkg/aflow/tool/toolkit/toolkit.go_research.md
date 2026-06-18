# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit.go

## Purpose
Registers an aflow tool that returns embedded C toolkit snippets, currently the race-condition toolkit.

## Important APIs, Types, and Functions
`ToolGetToolkit` registers `get-toolkit`. `getToolkitArgs.Name` selects a toolkit. `raceConditionToolkit` embeds `race_toolkit.h`. `getToolkit` returns the race toolkit or an unknown-toolkit bad-call error. `GetRaceToolkit` exposes the embedded header to Go callers.

## Control Flow
A simple name switch accepts exactly `race`; all other names fail with available toolkit guidance.

## State and Persistence Behavior
Read-only embedded asset. No runtime mutation.

## Dependencies and Integration Points
Depends on Go embed and `aflow`. Used by agents building C reproducers that need synchronization helpers.

## Risks and Test Signals
Risk is embedded header drift or missing toolkit names. `toolkit_test.go` compiles and runs C testdata to validate the embedded file's source counterpart.
