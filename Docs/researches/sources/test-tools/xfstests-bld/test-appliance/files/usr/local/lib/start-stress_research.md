# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/start-stress

Purpose: starts background stress workload for the appliance.

Important flow: a small shell wrapper that launches `stress` with configured/default CPU, IO, VM, or disk pressure options and records/daemonizes it for test runs that request stress conditions.

State and dependencies: depends on the `stress` package installed by image builders and runtime environment variables or arguments. It may leave background processes that tests or shutdown must clean.

Integration points: xfstests configurations and hooks can use it to add load while tests run.

Risks and test signals: resource pressure can amplify flakiness or hide root causes. Tests should verify process launch, option propagation, and cleanup behavior.
