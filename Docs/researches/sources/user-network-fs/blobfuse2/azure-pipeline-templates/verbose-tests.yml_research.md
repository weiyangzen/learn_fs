# sources/user-network-fs/blobfuse2/azure-pipeline-templates/verbose-tests.yml

## Purpose
This orchestration template runs the broadest set of E2E, auth, cache, mount, stress, and huge-list tests for one storage service/account combination.

## Important APIs, Types, and Functions
Parameters cover account endpoint/type/name/key/SAS, credential booleans, Azurite config, stress and huge-list inputs, distro name, quick flags, and verbose logging. It composes `e2e-tests.yml`, `e2e-tests-spcl.yml`, `mount-test.yml`, `stress-test.yml`, and `huge-list-test.yml`, and generates configs for key, SAS, Azure CLI, Azurite, block-cache, file-cache, LRU, empty-file, direct-IO, symlink, stress, and huge-list variants.

## Control Flow
It conditionally creates key, SAS, Azure CLI, and Azurite configs and runs E2E tests for enabled credential types. It always runs block-cache special E2E, then several file-cache/symlink/direct-IO special configs. If Azurite is enabled, it installs and starts Azurite with documented fake credentials. It generates a huge config, runs mount tests, stress tests, then regenerates config against the huge container and runs listing tests.

## State and Persistence Behavior
It writes many generated config files, may start an Azurite service and create a local emulator container, writes remote test data into Azure containers, uses shared mount/cache paths, and emits logs/artifacts through child templates.

## Dependencies and Integration Points
It is called by nightly base tests for block blob and ADLS. It depends on generated containers from `build.yml`, storage credentials, child templates, and repository config templates.

## Risks and Edge Cases
The parameter surface is large, and unused service principal parameters suggest drift. Config files are printed. Azurite uses public fake credentials intentionally. Failures in child templates with `continueOnError` can reduce strictness. Huge-list tests rely on a persistent preloaded container.

## Test Signals
Signals include successful E2E passes for enabled credentials, block/file cache special config passes, mount-test and stress-test completion, and huge-list output/counts.
