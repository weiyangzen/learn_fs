# sources/storage-engines/wiredtiger/test/cppsuite/src/component/component.cpp

Purpose: Implements the base lifecycle for cppsuite components.

Important APIs/types/functions: constructor records config/name, reads `enabled`, and computes sleep interval from config. `load` asserts enabled and logs. `run` loops while `_running`, calling virtual `do_work` and sleeping. `end_run` flips `_running` false. `finish` asserts not running and logs. Destructor deletes the owned configuration.

Control flow: expected order is load, run in a thread, end_run, finish. Derived components override `do_work` and sometimes `run`, `load`, or `finish`.

State and persistence: owns `_config`, `_name`, `_enabled`, `_running`, and `_sleep_time_ms`; no direct persistence.

Dependencies/integration: all cppsuite components inherit from this class and use `constants`/`logger`.

Risks and test signals: `_running` is `volatile bool`, not atomic, so cross-thread stop signaling relies on limited guarantees. Assertions catch lifecycle misuse in debug/assert-enabled builds.
