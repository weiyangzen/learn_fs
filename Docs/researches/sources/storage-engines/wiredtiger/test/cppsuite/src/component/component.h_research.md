# sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.h

Purpose: Declares the common four-stage component interface for cppsuite.

Important APIs/types/functions: `component` exposes `load`, `run`, `end_run`, pure virtual `do_work`, `enabled`, and `finish`; copy/assignment are deleted.

Control flow: subclasses are expected to perform setup in `load`, work in a run loop, respond to `end_run`, and validate/clean up in `finish`.

State and persistence: holds enable/running flags, throttle interval, owned config pointer, and component name.

Dependencies/integration: uses `configuration`; inherited by timestamp manager, metrics monitor, operation tracker, and workload manager.

Risks and test signals: config ownership is transferred into the component, so callers must not reuse/delete it. Subclasses overriding `run` must preserve lifecycle expectations.
