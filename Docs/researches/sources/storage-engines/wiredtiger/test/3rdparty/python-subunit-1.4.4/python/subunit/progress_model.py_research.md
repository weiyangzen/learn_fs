# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/progress_model.py

## Purpose

`progress_model.py` models nested progress directives from subunit streams and provides an aggregate position/width suitable for UIs.

## Important APIs, Types, and Functions

`ProgressModel` exposes `adjust_width(offset)`, `advance()`, `push()`, `pop()`, `set_width(width)`, `pos()`, and `width()`. Internal `_tasks` entries are mutable lists containing current position, width, and the overall position/width at push time.

## Control Flow

Construction pushes an initial task with unknown width. Top-level `advance` and width adjustments update the current task directly. `push` creates a nested subtask preserving overall progress. `pos()` and `width()` scale the saved outer progress by the nested width when nested tasks exist; if current nested width is zero, scaling uses one to preserve overall progress.

## State and Persistence Behavior

All state is in `_tasks`. There is no persistence or external I/O. `pop()` removes the current task without underflow checks.

## Dependencies and Integration Points

The module has no imports. `subunit2gtk.py` uses it to turn protocol progress events into a GTK progress bar.

## Risks and Test Signals

Risks are arithmetic edge cases around zero widths, nested scaling, and popping too far. `test_progress_model.py` covers initial `0/0`, advancing unknown totals, setting and adjusting widths, push/pop behavior, and nested scaling.
