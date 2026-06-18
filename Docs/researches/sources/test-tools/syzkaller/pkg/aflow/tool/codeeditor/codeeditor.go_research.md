# sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor.go

## Purpose
Implements the `codeeditor` aflow tool that lets an agent apply one source edit by replacing an exact or fuzzy multi-line snippet in a scratch kernel source tree.

## Important APIs, Types, and Functions
`Tool` is an `aflow.NewFuncTool`. `state` supplies `KernelScratchSrc`; `args` supplies `SourceFile`, `CurrentCode`, and `NewCode`. `codeeditor` validates paths and source-file status, normalizes trailing newlines, splits file/snippet/replacement with `bytes.Lines`, and delegates matching to `replace`. `replace` scans line slices and can match exactly or with whitespace/blank-line tolerant fuzzy comparison.

## Control Flow
The tool rejects path traversal, missing/non-source files, and empty current snippets. It first attempts exact replacement, then fuzzy replacement if no exact match exists. Zero matches and multiple matches are bad calls; one match is written back with `osutil.WriteFile` if the data changed.

## State and Persistence Behavior
It mutates only the selected file under `KernelScratchSrc`. It does not update codesearch indexes, which is explicitly warned in the tool description.

## Dependencies and Integration Points
Depends on `aflow` for tool registration/errors, `codesearch.IsSourceFile` for source filtering, and `osutil` for filesystem helpers. Integrated into patch-generating agent workflows alongside `patchdiff`.

## Risks and Test Signals
Fuzzy matching can delete or replace more lines than expected if context is underspecified, so multiple-match rejection is important. Tests cover traversal, missing/non-source files, empty snippets, no-op edits, exact/fuzzy replacements, deletion, duplicate matches, and fuzzing of arbitrary file/snippet data.
