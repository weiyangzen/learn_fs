# sources/test-tools/syzkaller/pkg/aflow/tool/codeexpert/codeexpert.go

## Purpose
Defines an LLM-backed `codeexpert` tool for complex Linux kernel source-code reasoning.

## Important APIs, Types, and Functions
`New(enableGit bool)` returns an `*aflow.LLMTool` configured with name, model, task type, description, instruction, and tools. It selects codesearch and grepper always, and gitlog tools only when `enableGit` is true. Constants hold the public description and instruction fragments.

## Control Flow
Construction concatenates instruction fragments depending on git availability. With git enabled it also adds history-source guidance and restrictions; without git it only exposes source search tools.

## State and Persistence Behavior
No persistent state. It creates tool metadata and instruction strings for runtime use.

## Dependencies and Integration Points
Depends on `aflow`, `codesearcher`, `grepper`, and `gitlog`. It is meant to be invoked by other agents when a kernel question is too complex for direct local tools.

## Risks and Test Signals
Risks are prompt drift, overbroad git usage, or missing tools when git is disabled. There is no direct test in this subset; integration tests should verify tool lists and instruction assembly.
