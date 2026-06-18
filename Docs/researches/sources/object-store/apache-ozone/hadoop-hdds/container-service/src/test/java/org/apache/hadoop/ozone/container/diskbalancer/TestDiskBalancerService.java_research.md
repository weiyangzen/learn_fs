# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerService.java

## Purpose
Tests `DiskBalancerService` lifecycle, config refresh validation, default policy initialization, bytes-to-move calculation, concurrency limits, info persistence, stale tmp cleanup, threshold validation, and movable container state parsing.

## Important APIs, Types, And Functions
Uses `DiskBalancerService.refresh`, `getTasks`, `calculateBytesToMove`, `start`, `shutdown`, `DiskBalancerInfo`, `DiskBalancerYaml`, `DiskBalancerConfiguration`, mocked `ContainerChoosingPolicy`, and `DiskBalancerServiceTestImpl`.

## Control Flow
Setup creates two mock-usage data volumes and Schema V3 DB instances. Tests refresh running/stopped info, reject invalid values, assert default policy, compute bytes to move for parameterized imbalance cases, schedule tasks up to thread limits, validate info-file directory and write failures, and start the real service to clean stale diskBalancer tmp dirs with initialized and uninitialized `tmpDir`.

## State And Persistence
Real temp volume dirs, DB instances, task queues, in-progress container IDs, `DiskBalancerInfo`, YAML info files, stale tmp trees, and BlockUtils cache cleanup are involved.

## Dependencies And Integration Points
Integrates volume sets, key-value handlers, container metrics, checksum manager, Ozone container mocks, background task queues, layout/schema parameterization, volume calculations, and HDDS/Ozone configs.

## Risks And Edge Cases
Touches concurrency, filesystem persistence, and startup cleanup. Log text confirms thread-limit behavior. Movable-state parsing intentionally rejects blank, lowercase, unknown, and non-movable states.

## Test Signals
Service info fields, invalid refresh exceptions, policy type, bytes-to-move tolerance, task counts, in-progress counts, YAML equality, IO exception prefixes, stale directory absence, threshold exceptions, and parsed state sets validate behavior.
