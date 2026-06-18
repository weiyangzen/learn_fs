# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/filesystem.go

## Purpose
Provides lightweight filesystem-style source browsing tools for aflow agents: directory index and bounded file reads.

## Important APIs, Types, and Functions
Exports `ToolDirIndex`, `ToolReadFile`, and `FilesystemTools`. `fsState` carries `KernelSrc`; `getSrcDir` validates it. `dirIndex` returns direct subdirectories and source files. `readFile` returns up to the codesearch layer's capped slice of file contents.

## Control Flow
Both tools resolve the root from state, then call `codesearch.DirIndex` or `codesearch.ReadFile` over that root. Errors from missing state or invalid paths propagate.

## State and Persistence Behavior
Read-only. No cache, no mutation, no durable state.

## Dependencies and Integration Points
Depends on `aflow` and `pkg/codesearch`. These tools are included in the larger `codesearcher.Tools` set and codeexpert.

## Risks and Test Signals
Risk is accidental exposure outside source roots, delegated to codesearch path handling. The 100-line cap is important to bound LLM context. Direct tests are absent in this subset.
