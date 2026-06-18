# sources/storage-engines/wiredtiger/test/suite/test_prepare20.py

## Purpose

Demonstrates an application-level log replay strategy for unstable prepared transactions across crash recovery.

## Important APIs, Control Flow, and State

`test_prepare20` uses a logged connection but a data file with `log=(enabled=false)` and a separate logged application log table. Helpers record logical operations: begin, write, prepare timestamp, prepare, commit timestamp, durable timestamp, and commit. The test commits baseline A at timestamp 10, logs and commits B at 22/25, optionally checkpoints at varied stable timestamps, logs C prepared at 30 and optionally commits it at 32/35, optionally checkpoints again, then simulates crash restart. `log_replay` scans the log, ignores transactions without prepare/commit evidence, starts replay transactions with `roundup_timestamps=(prepared=true)`, repairs durable timestamps if they are not beyond stable, and commits any prepared-but-uncommitted transaction with recorded times.

## Dependencies, Risks, and Test Signals

Dependencies are `simulate_crash_restart`, scenarios over key format, checkpoint timing, and commit-before-crash state. Risks include replaying unprepared partial work, double-writing stable data, or using durable timestamps below stable. Signals are reads at timestamps 15/25/35 and expected replay counts based on checkpoint timing.
