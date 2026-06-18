# sources/user-network-fs/gcsfuse/cfg/types.go

## Purpose
`cfg/types.go` defines custom scalar types and parse/validation helpers used by the generated configuration system. These types bridge textual CLI/YAML values and strongly typed config fields for octal permissions, protocol choices, DirectPath fallback strategy, log severity, resolved filesystem paths, optimization inputs, and bucket-type classification.

## Important APIs And Types
`Octal` implements `encoding.TextUnmarshaler` and marshaling by parsing and formatting base-8 values for `file-mode` and `dir-mode`. `Protocol` accepts case-insensitive `http1`, `http2`, and `grpc`. `DirectPathStrategy` accepts `direct-path-only` and `direct-path-with-fallback`. `LogSeverity` accepts `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `OFF`, with `Rank()` exposing numeric ordering for logger setup. `ResolvedPath` resolves user paths through `util.GetResolvedPath`, including parent-process directory behavior for daemonized runs. `OptimizationInput` carries runtime dimensions for optimizations, currently `BucketType`. `BucketType` enumerates `zonal`, `pirlo`, `hierarchical`, and `flat`, with `IsValid()` for domain checks.

## Control Flow And State
Each custom type's `UnmarshalText` normalizes or validates a byte slice and writes the parsed value to the receiver. Invalid enum values return descriptive errors that surface through Cobra/Viper or config-file unmarshalling. `ResolvedPath` may consult process/environment context through `util.GetResolvedPath`, but the file itself does not store persistent state. `LogSeverity.Rank()` reads a package map and returns `-1` for unknown values, which allows defensive callers to avoid panics.

## Dependencies And Integration
The file depends on `strconv`, `strings`, `slices`, `fmt`, and `internal/util`. The decode hooks used by `cmd/root.go` route YAML and flag values through these `UnmarshalText` methods. `cmd/mount.go` uses `LogSeverity.Rank()` to decide whether to install FUSE error/debug loggers, and `cmd/legacy_main.go` passes `Protocol` and `DirectPathStrategy` into storage client configuration.

## Risks And Test Signals
Risks include enum drift with `params.yaml`, especially if the YAML type list and actual custom types diverge. `Octal` stores parsed permission bits as an integer, so consumers must remember that decimal display differs from octal source syntax. `ResolvedPath` behavior depends on environment forwarding in daemon mode. `cmd/datatypes_parsing_test.go` and `cfg/validate_test.go` cover CLI/config parsing of octal, protocol, log severity, resolved paths, and severity ranking.
