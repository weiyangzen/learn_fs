# sources/sync-backup/bup/dev/have-pylint

## Purpose
Small probe for whether pylint imports successfully under bup's configured Python runtime.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec` and attempts `import pylint`.

## Control Flow
Exits 0 if import succeeds, 1 on `ImportError`, and 2 with error text for other exceptions.

## State and Persistence Behavior
No persistence.

## Dependencies and Integration Points
Used by build/lint configuration to distinguish absent pylint from broken pylint.

## Risks and Test Signals
Signal is exit status. Risk is import side effects from installed pylint/plugin environment.
