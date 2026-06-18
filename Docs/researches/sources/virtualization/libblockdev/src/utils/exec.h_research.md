# File Research: sources/virtualization/libblockdev/src/utils/exec.h

This public header declares execution and progress-reporting utilities.

Types:
- `BDUtilsProgStatus`: started, progress, finished.
- `BDUtilsProgFunc`: callback receiving task ID, status, completion percent, and message.
- `BDUtilsProgExtract`: callback that parses a line from stdout/stderr and optionally extracts progress.

Error enum:
- `BDUtilsExecError` includes generic failure, no output, invalid version, utility unavailable, unknown version, low version, utility check error, feature check error, and feature unavailable.

Declared APIs:
- Command execution with or without progress.
- Output capture with or without progress.
- Execution with stdin input.
- Version comparison and utility version checks.
- Progress callback initialization, thread-local override, thread muting, and explicit progress reporting.
- Task ID allocation and task status logging.
- String-to-file write helper.

Research relevance:
- The comments document output ordering caveats: stdout and stderr are read simultaneously with no guaranteed ordering for progress extraction.
