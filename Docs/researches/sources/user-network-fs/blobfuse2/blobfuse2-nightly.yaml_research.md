# sources/user-network-fs/blobfuse2/blobfuse2-nightly.yaml

## Purpose
This is the main daily Blobfuse2 validation pipeline. It builds and tests across distros, account types, auth modes, cache modes, proxy/MSI paths, data integrity, xload, health monitor, FIO, scenarios, RMAN, and optional Linux/Git workloads.

## Important APIs, Types, and Functions
Parameters toggle `base_test`, `exhaustive_test`, non-Ubuntu distros, `fio_test`, `scenario_tests`, `rman_backup_test`, `linux_git_test`, `proxy_test`, `msi_test`, `quick_stress`, `verbose_log`, and `healthmon`. It composes most templates in `azure-pipeline-templates`, especially `build.yml`, `verbose-tests.yml`, `invalid-command-tests.yml`, `verify-auth.yml`, `data-integrity.yml`, `e2e-tests-xload.yml`, `bfusemon.yml`, `fio-data-integrity.yml`, `scenario.yml`, `rman-backup*.yml`, `linux-git.yml`, and `cleanup.yml`.

## Control Flow
The daily schedule starts with `BuildAndTest` when enabled. Block Blob and ADLS jobs build and optionally run exhaustive verbose tests over Ubuntu 20, Ubuntu 22, and ARM64. Optional proxy tests generate proxy configs and validate key/SAS auth through E2E/auth templates. Optional MSI tests build with MSI enabled and verify block/ADLS MSI mounts. Later stages validate file cache and block cache data integrity for block and ADLS, xload preload behavior, health monitor output, optional FIO integrity workloads, scenario tests, RMAN simulation and Oracle XE backup tests, and optional Linux compile/Git clone workloads.

## State and Persistence Behavior
Each job creates Azure containers, mount/cache directories, generated configs, logs, data files, and sometimes persistent huge-list container reads. Cleanup stages usually delete containers except RMAN cleanup leaves containers undeleted in its shown configuration. Variable group `NightlyBlobFuse` supplies credentials and account names.

## Dependencies and Integration Points
This pipeline is the integration hub for the Azure DevOps template library. It depends on many custom self-hosted pools, distro-specific images, Azure storage accounts, Oracle agents, optional huge containers, proxy tooling, Azurite in child templates, and Go test suites.

## Risks and Edge Cases
The YAML contains a duplicated `matrix:` key in the Healthmon stage, which may be invalid or confusing. Many stages are conditionally enabled, so default coverage omits FIO and Linux/Git workloads. Some child templates use `continueOnError`, broad process kills, and config printing. The pipeline is sensitive to stale self-hosted agent state.

## Test Signals
Signals are stage-level pass/fail across all enabled parameter combinations, created/deleted container balance, no stale mounts, successful data checksum comparisons, E2E and stress Go test passes, RMAN integrity success, and clean logs/traces.
