# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce.go

## Purpose
Implements the `reproduce-crash` aflow tool that validates and optionally executes syz repro programs in a VM with coverage.

## Important APIs, Types, and Functions
`Reproduce` registers the tool. `ReproduceArgs` carries `ReproSyz`; `ReproduceResult` carries reproduced bug title/report and cached execution ID. `reproduceState` stores target, kernel, image, VM, and syzkaller paths. `reproduce` parses the program via `prog.GetTarget` and `Deserialize`, then calls `crash.ReproduceFuncWithCoverage` when VM config is present.

## Control Flow
Empty programs and parse errors become bad calls. Without image or VM state, the tool only validates compilation/parsing and returns empty success. With VM state, it builds crash reproduction args, executes with coverage, returns cached ID on did-not-crash, and returns report details on crash.

## State and Persistence Behavior
Execution results and coverage are cached by crash reproduction code and referenced by `ExecutionCachedID`. This function itself does not write source files.

## Dependencies and Integration Points
Depends on `aflow`, `crash`, `prog`, and imported sys descriptions. Integrated with coverage tools via cached IDs.

## Risks and Test Signals
Risks include unsafe/unavailable VM configs, parse strictness, and treating non-crashing executions as non-errors. Tests cover empty, valid, syntax-invalid, and unknown-syscall programs in validation-only mode.
