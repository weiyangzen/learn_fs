# sources/storage-engines/foundationdb/fdbrpc/sim_validation.cpp

## Purpose
`sim_validation.cpp` provides debug-only simulation validation helpers for tracking committed/restored version bounds and version timestamps. It is used to detect durability and relocation regressions during simulated runs, while automatically disabling itself outside simulation or when the active simulation policy says version validation should not run.

## Important APIs, Types, And Functions
The file owns static validation state: `validationData` maps `UID` plus `"min"`/`"max"` suffix to committed-version bounds, `timedVersionsValidationData` maps versions to maximum allowed times, `disabledMachines` records IDs excluded from version checking, and `checkRelocationDuration` toggles relocation duration checks. Public debug helpers include `debug_setVersionCheckEnabled`, `debug_advanceCommittedVersions`, `debug_advanceMinCommittedVersion`, `debug_advanceMaxCommittedVersion`, `debug_checkRestoredVersion`, `debug_checkMinRestoredVersion`, `debug_checkMaxRestoredVersion`, `debug_removeVersions`, `debug_versionsExist`, `debug_setCheckRelocationDuration`, `debug_isCheckRelocationDuration`, `debug_advanceVersionTimestamp`, and `debug_checkVersionTime`.

## Control Flow
Every externally visible validation path first checks `versionValidationDisabled()`, which returns true outside simulation or when the simulation policy disables version validation. Advance functions update monotonic min/max records unless the machine is disabled. Check functions compare restored versions against the recorded min or max using a sign flip: min checks fail when restored is lower than recorded min, max checks fail when restored is higher than recorded max. Timestamp checks report when a checked time exceeds the recorded timestamp for that version.

## State And Persistence Behavior
All state is static process memory and is not persisted. `debug_setVersionCheckEnabled(false)` also removes any existing version records for that ID. Because keys are string-concatenated `UID` values plus suffixes, state is shared globally within the process and assumes the suffix vocabulary stays limited to `"min"` and `"max"`.

## Dependencies And Integration Points
The code depends on `fdbrpc/sim_validation.h`, `TraceFileIO`, `flow/network.h`, and `fdbrpc/simulator.h`. Its main integration point is simulation policy via `g_simulator->getSimulationPolicy()->shouldRunVersionValidation()`, and its output is trace events named with caller-provided context plus suffixes such as `UnknownVersion`, `DurabilityError`, `UnknownTime`, and `VersionTimeError`.

## Risks And Test Signals
Unknown versions only emit warnings and return false, so missing instrumentation may hide a durability issue. Disabled machines suppress both updates and checks. The global static maps are not isolated per simulation run unless process lifetime resets them. Useful signals are `DurabilityError` and `VersionTimeError` trace events under simulation policies that enable validation, plus coverage of disabled-machine behavior, missing version warnings, timestamp checks, and policy-disabled/no-simulation no-op paths.
