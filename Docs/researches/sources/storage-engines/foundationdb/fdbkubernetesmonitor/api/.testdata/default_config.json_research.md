# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/default_config.json

## Purpose
This JSON fixture defines a sample `ProcessConfiguration` for API tests of the Kubernetes monitor.

## Important APIs, Types, And Functions
The fixture sets version `6.3.15` and an `arguments` array combining literal values, environment lookups, process-number arithmetic, and concatenation. It covers `--cluster-file`, public/listen addresses, datadir, class, and locality flags.

## Control Flow
Tests decode the JSON into `ProcessConfiguration`, then `GenerateArguments(1, env)` expands environment values and process-number expressions. The port expression uses process number `1`, multiplier `2`, and offset `4499` to produce `4501`.

## State And Persistence Behavior
This is static test data. It references `.testdata/fdb.cluster` and `.testdata/data/<process>` paths but does not create them by itself.

## Dependencies And Integration Points
It integrates with `config_test.go` and the JSON unmarshalling behavior of `Version`, `ProcessConfiguration`, and `Argument`.

## Risks And Edge Cases
Because this fixture is a representative default config, changes to argument ordering or defaults can break exact-element tests. It does not exercise IP-list selection or `runServers`.

## Test Signals
The key signal is exact generated argument order and values for the provided environment map, plus version decoding to major/minor/patch fields.
