# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_progress_model.py

## Purpose

`test_progress_model.py` validates the nested arithmetic of `ProgressModel`.

## Important APIs, Types, and Functions

`TestProgressModel.assertProgressSummary` checks `pos()` and `width()`. Individual tests cover initial unknown progress, advancing with unknown width, setting and adjusting width, preserving position, push/pop behavior, and nested subtask scaling.

## Control Flow

Each test creates a fresh model, performs a short sequence of progress operations, and asserts the resulting aggregate position and total.

## State and Persistence Behavior

All state is in the `ProgressModel` instance. There is no I/O.

## Dependencies and Integration Points

It depends on `unittest` and `subunit.progress_model.ProgressModel`. It indirectly protects GTK progress display behavior.

## Risks and Test Signals

The test suite captures the intended semantics for zero-width tasks and nested progress scaling. It does not cover invalid `pop()` underflow or negative widths beyond adjustment back to zero.
