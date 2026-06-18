# sources/test-tools/syzkaller/pkg/aflow/flow/common/common.go

## Purpose

`common.go` provides reusable workflow helpers, chiefly the standard set of code access tools and shared prompt instruction discouraging source-code assumptions.

## Important APIs, Types, and Functions

`CodeAccessTools` is the default tool slice with git support. `CodeAccessToolsWithGit(enableGit bool)` creates a `codeexpert` LLM tool and combines its inner tools with the expert tool itself through `aflow.Tools`. `InstructionDontMakeAssumptionsAboutSourceCode` is a prompt fragment used by multiple workflows.

## Control Flow

Tool construction calls `codeexpert.New(enableGit)`, then returns a flattened tool list. Prompt constants are concatenated or substituted by other files.

## State and Persistence Behavior

Tool instances are package-level values and persist for the process. They do not themselves store workflow state here; tool execution state is handled by the tool implementations and aflow context.

## Dependencies and Integration Points

It depends on aflow tool composition and `tool/codeexpert`. Assessment, repro, patching, and reproc flows use these helpers.

## Risks and Edge Cases

Package-level `CodeAccessTools` creates tool instances at init time; duplicate registration behavior must be compatible with tests and MCP registration. The shared instruction names concrete tools such as `{{.toolGrepper}}`, so templates must provide matching tool template variables.

## Test Signals

Common prompt substitution is tested in `prompts_test.go`; tool composition is indirectly checked by flow registration tests.
