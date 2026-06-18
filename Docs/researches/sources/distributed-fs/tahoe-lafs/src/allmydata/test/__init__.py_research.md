# sources/distributed-fs/tahoe-lafs/src/allmydata/test/__init__.py

## Purpose
Applies global test-suite side effects for Tahoe-LAFS. It disables Foolscap incident reporting, configures Hypothesis, improves Foolscap listener error diagnostics, applies Windows fixups, and enables Eliot logging for tests.

## Important APIs, Types, And Functions
`NonQualifier` suppresses Foolscap incidents. `disable_foolscap_incidents()` installs it. `_configure_hypothesis()` registers a CI profile that suppresses slow-data health checks and disables deadlines, then loads the profile selected by `TAHOE_LAFS_HYPOTHESIS_PROFILE`. `logging_for_pb_listener()` monkey-patches Foolscap `Listener` construction and startup to record creation stacks and report listen failures. It also opens `eliot.log` with `AnyBytesJSONEncoder`.

## Control Flow
Importing the package immediately disables incidents, configures Hypothesis, patches Foolscap listeners, runs Windows initialization if needed, and starts Eliot file logging. The file is not an API module; its behavior is intentionally import-time test setup.

## State And Persistence
It mutates process-global Foolscap logger state, Hypothesis settings, Foolscap `Listener` methods, Windows process state, and creates or appends to `eliot.log` in the current working directory.

## Dependencies And Integration Points
Depends on Foolscap logging/listener internals, Twisted logging/service APIs, Hypothesis, Windows fixups, Eliot, and Tahoe JSON-bytes encoding. It affects all Trial tests importing `allmydata.test`.

## Risks And Test Signals
Global monkey patches can hide production-like behavior or interact badly with other test frameworks. Opening `eliot.log` at import time can leak file handles or write in surprising directories. Test signals are cleaner Trial shutdowns, no Foolscap incident timers, useful listener failure tracebacks, Hypothesis profile selection via environment, and absence of DirtyReactor failures caused by incident trailing delays.
