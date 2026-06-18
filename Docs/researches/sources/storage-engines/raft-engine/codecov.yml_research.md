# sources/storage-engines/raft-engine/codecov.yml

## Purpose
Configures Codecov coverage status thresholds for raft-engine.

## Important APIs, Types, And Functions
The YAML defines project and patch coverage statuses. Both use `target: auto` and `threshold: 3%`. The ignore list excludes `stress` and `ctl`.

## Control Flow
After CI uploads `coverage.lcov`, Codecov evaluates project-wide and patch-level coverage against automatic baselines while allowing a three percent tolerance.

## State And Persistence Behavior
No runtime persistence is involved. The file affects repository quality-gate metadata and pull request statuses.

## Dependencies And Integration Points
Integrates with `.github/workflows/rust.yml`, the grcov-generated lcov file, and Codecov's status checks. Ignoring `ctl` means CLI code coverage does not affect the main engine threshold.

## Risks And Edge Cases
The broad threshold can permit meaningful coverage drops. Excluding `stress` and `ctl` is reasonable for non-library code but can hide regressions in tooling unless covered elsewhere.

## Test Signals
Signals are Codecov project and patch checks after coverage upload.
