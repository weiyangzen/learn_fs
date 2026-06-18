# sources/sync-backup/borg/scripts/errorlist.py

Purpose: Generates an error/warning class list for documentation by introspecting Borg's `Error`, `BackupError`, and `BorgWarning` class hierarchies and their exit/mcode assignments.

Important APIs/types/functions: Defines recursive `subclasses(cls)`. Imports `borg.archiver` for side effects so subclasses are registered, constants `EXIT_ERROR_BASE`, `EXIT_WARNING_BASE`, `EXIT_SIGNAL_BASE`, and classes from `borg.helpers`. Uses class attributes `traceback`, `exit_mcode`, `__doc__`, `__module__`, and `__qualname__`.

Control flow: Initializes free error return-code set 3..99 and warning set 100..127. Iterates sorted error classes, prints metadata/docs, removes assigned specific codes, tracks generic rc 2 classes, and flags duplicate/invalid codes. Repeats for warnings/backup warnings, tracking generic rc 1 classes, then prints free/generic summaries.

State and persistence: No file writes; output is printed to stdout for documentation capture/review. It mutates local tracking sets only.

Dependencies and integration points: Depends on importing the full Borg archiver module without triggering unwanted runtime behavior. Integrates with return-code documentation and CI/release checks for unique specific codes.

Risks: If some modules defining subclasses are not imported by `borg.archiver`, their classes will be absent. `indent(cls.__doc__, ...)` assumes docstrings are present; missing docstrings could fail or produce poor docs.

Test signals: Run under `PYTHONPATH=src python scripts/errorlist.py`, check no `ERROR:` lines, verify expected free ranges, and compare generated docs after adding new exception/warning classes.
