# sources/user-network-fs/gcsfuse/cfg/shared/types.go

## Purpose
`cfg/shared/types.go` defines small shared data structures used to deserialize optimization metadata from the parameter registry. It exists in a `shared` subpackage so optimization schema types can be reused without importing the entire cfg package or creating dependency cycles.

## Important Types
`ProfileOptimization` contains a profile `Name` and generic `Value`. `MachineBasedOptimization` contains a machine `Group` and generic `Value`. `BucketTypeOptimization` contains a `BucketType` string and generic `Value`. `OptimizationRules` groups the three optimization lists under YAML keys `machine-based-optimization`, `bucket-type-optimization`, and `profiles`. All value fields are `any` because YAML defaults and overrides may be booleans, strings, integers, durations, or generated expression-like defaults depending on the parameter.

## Control Flow And State
There is no executable control flow, mutation, or persistence in this file. Its state model is purely serialized YAML data flowing from `cfg/params.yaml` into optimization application logic elsewhere in the cfg package.

## Dependencies And Integration
The file has no imports. It is integrated by YAML parsing of `params.yaml`, especially entries that tune metadata cache, file cache, implicit dirs, rename limits, FUSE kernel parameters, and write behavior based on machine groups, bucket type, or profiles such as `aiml-training`, `aiml-serving`, and `aiml-checkpointing`.

## Risks And Test Signals
Because `Value` is untyped, downstream code must safely coerce optimization values to the destination config field type. Any mismatch between YAML value shape and parameter type can fail late or produce unexpected behavior. Test signal comes indirectly from optimization and config command tests; this file has no direct unit tests because its behavior is structural.
