# sources/distributed-fs/tahoe-lafs/misc/build_helpers/run-deprecations.py

## Purpose

This Twisted-based wrapper runs a command, captures stdout/stderr, and fails the build if relevant Python deprecation warnings are seen. It can restrict warning collection to a specific package path and optionally write the collected warnings to a file.

## Important APIs, Types, and Functions

`Options` parses `--warnings`, `--package`, command, and command args. `RunPP` is a `ProcessProtocol` that mirrors child output to parent stdout/stderr while buffering bytes. `make_matcher` builds a regex matcher for deprecation-looking file/line records. `run_command` resolves the executable with `twisted.python.procutils.which`, spawns it, de-duplicates matching lines, writes the warnings log, and exits with command status or failure.

## Control Flow

`task.react(run_command)` drives the whole script. The child process runs under `reactor.spawnProcess`. After process completion, the script scans both buffered streams, preserving order within each stream and suppressing duplicates. Any warning forces `sys.exit(1)` regardless of the command's own return code; otherwise the wrapper exits with the child signal or exit code.

## State, Dependencies, Integration, Risks, and Tests

State is transient buffers plus optional warnings output file. Dependencies are Twisted reactor/process APIs and Python encoding settings. Integration is buildbot/test commands run with warnings enabled. Risks include regex overmatching any `.py:line:` record, decoding with `sys.stdout.encoding`, stdout/stderr ordering not preserved across streams, and signal exit values being used directly. Tests should use child commands emitting duplicate warnings, non-warning tracebacks, package-filtered paths, nonzero exits, and missing executables.
