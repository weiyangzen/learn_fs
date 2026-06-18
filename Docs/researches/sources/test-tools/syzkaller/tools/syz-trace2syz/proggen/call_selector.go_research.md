# sources/test-tools/syzkaller/tools/syz-trace2syz/proggen/call_selector.go

## Purpose
This file selects the best syzkaller syscall description variant for a parsed strace syscall when multiple descriptions share a call name or when `open`-family calls need special mapping.

## Important APIs, types, and functions
- `discriminatorArgs` lists syscall argument positions used to distinguish variants by constants, flags, resources, or strings.
- `openDiscriminatorArgs` lists filename argument indexes for `open`, `openat`, and `syz_open_dev`.
- `callSelector` interface exposes `Select`.
- `newSelectors` returns default and open selectors sharing `selectorCommon`.
- `selectorCommon.matchFilename` compares syzkaller string patterns with strace paths, allowing `#` to match digits and returning a device ID.
- `callSet` caches non-automatic target syscalls by call name.
- `openCallSelector.Select` and `matchOpen` specialize open/openat/syz_open_dev matching and argument rewrites.
- `defaultCallSelector.Select` and `matchCall` score variant matches using target argument types and return-cache resource tracking.

## Control flow
Selectors are tried by callers in the returned order. The default selector considers only calls listed in `discriminatorArgs` and chooses the highest positive score. The open selector checks every open-family target variant; when an `open` strace call matches `openat`, it prepends `AT_FDCWD`, and when it matches `syz_open_dev`, it may insert the extracted device ID.

## State and persistence behavior
State is in-memory: target pointer, return cache, and call-set cache. Selectors may mutate the parsed syscall's `Args` slice when translating `open` to `openat` or `syz_open_dev`.

## Dependencies and integration points
Depends on `prog.Target` syscall metadata, parser IR types, and a package-local `returnCache` abstraction for resource arguments. It is part of the trace-to-program generation pipeline.

## Risks and edge cases
`openCallSelector.matchOpen` type-asserts the strace filename arg to `*parser.BufferType`; malformed/non-string args can panic. `matchFilename` concatenates all digits matched by multiple `#` placeholders into one number, which is tested but may be surprising. Selector order means default selection is attempted before open selection; caller behavior determines whether later selectors can override nil only. Scores are heuristic and may choose wrong variants for ambiguous flags/resources.

## Test signals
`call_selector_test.go` covers filename matching, including `#` digit extraction and NUL trimming. There is no direct test for variant scoring, open argument rewrites, resource matching, or panic cases.
