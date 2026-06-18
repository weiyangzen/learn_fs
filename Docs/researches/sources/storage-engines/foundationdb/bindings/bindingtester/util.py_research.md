# sources/storage-engines/foundationdb/bindings/bindingtester/util.py

## Purpose
`bindingtester/util.py` contains small process-level utilities for the bindingtester: logger configuration/access, signal name lookup, dynamic import of test subclasses, and conversion of an `fdb.Subspace` raw key back to a tuple.

## Important APIs, Types, And Functions
- `initialize_logger_level(logging_level)` maps string levels `DEBUG`, `INFO`, `WARNING`, and `ERROR` to Python logging constants and applies them to the bindingtester logger.
- `get_logger()` returns `logging.getLogger("foundationdb.bindingtester")`.
- `signal_number_to_name(signal_num)` scans the `signal` module for matching signal constants and returns the sole name or the numeric string.
- `import_subclasses(filename, module_path)` imports all sibling `.py` modules except `__init__.py`.
- `subspace_to_tuple(subspace)` unpacks `subspace.key()` with `fdb.tuple.unpack()` and raises a bindingtester-specific error if the prefix is not tuple-encoded.

## Control Flow
Most functions are direct helpers. `import_subclasses()` computes a directory from `filename`, iterates Python files with `glob`, derives module names, and imports them for side-effect class registration. `subspace_to_tuple()` logs the original exception before raising a clearer limitation message.

## State And Persistence Behavior
There is no database persistence. Logger level changes persist process-wide. Importing subclasses mutates Python module/import state.

## Dependencies And Integration Points
It depends on Python `logging`, `signal`, `os`, `glob`, and `fdb`. Directory tests use `subspace_to_tuple()` to build tuple-encoded prefix-log keys; harness startup can use `import_subclasses()` to discover tests.

## Risks And Edge Cases
`initialize_logger_level()` accepts only uppercase level names and raises `ValueError` otherwise. `signal_number_to_name()` can return a number if aliases match multiple constants. `subspace_to_tuple()` prevents tests from using raw prefixes that are not valid tuple encodings, which is an explicit bindingtester limitation.

## Test Signals
Indirect signals appear through test discovery, logging, and directory prefix logging. Failures in `subspace_to_tuple()` surface quickly when a workload tries to use unsupported subspace prefixes.
