# sources/sync-backup/bup/lib/__init__.py

## Purpose
Empty package marker for bup's top-level `lib` import path.

## Important APIs, Types, and Functions
No code, exports, or runtime symbols.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Allows Python import machinery to treat `lib` as a package when repository-local paths are inserted during tests or execution.

## Risks and Test Signals
Risk is only packaging/import layout drift. Test signal is successful imports from the repository's `lib` tree.
