# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/check/check.go

Purpose: shared utility package for command execution, filesystem checks, file copying, and log-aware error handling.

Important APIs: `Run`, `Output`, `LimitedRun`, `LimitedOutput`, `CombinedOutput`, `CreateDir`, `FileExists`, `DirExists`, `ReadLines`, `CopyFile`, `Panic`, `NoError`, and `ContainsStr`. Constants set server source root and a capped/rate-limited external command budget.

Control flow/state: command helpers set working directory, merge provided environment into `os.Environ`, and attach stdout/stderr writers. Limited helpers use a channel cap of 12 and a rate limiter of one command per second to reduce concurrent `gce-xfstests` pressure. `ReadLines` loads a whole file and filters empty lines. `CopyFile` removes existing destination before rewriting.

Dependencies: `os/exec`, `context`, `golang.org/x/time/rate`, logrus, and filesystem APIs.

Risks and test signals: `LimitedRun` and `LimitedOutput` can leak cap slots if `limiter.Wait` returns after sending to the cap channel. `CopyFile` is not atomic. `ReadLines` is whole-file and unsuitable for very large files. Tests should cover env merging, rate/cap behavior under errors, and file helper edge cases.
