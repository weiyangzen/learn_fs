# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/progress.h

## Purpose

Declares internal progress display APIs for command-line tools.

## Main Contents

- Forward declaration of opaque `struct tools_progress`.
- Global progress enable/disable/query functions.
- `tools_progress_start()` begins a named progress item with long/short names and either bounded count or spinner mode.
- `tools_progress_step()` increments completed work, with comments documenting display throttling.
- `tools_progress_stop()` removes and frees a progress item.

## Dependencies and Integration

- Used by tools that support a `--progress` style option.
- Designed to coexist with verbose output functions, which are expected to interact correctly with active progress display.

## Research Notes

- Supports nested progress items so top-level and sub-action progress can display together.
