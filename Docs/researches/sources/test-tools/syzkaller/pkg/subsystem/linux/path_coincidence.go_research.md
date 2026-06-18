# sources/test-tools/syzkaller/pkg/subsystem/linux/path_coincidence.go

## Purpose

`path_coincidence.go` walks a Linux source tree, matches relevant source files against subsystem path rules, and builds the `CoincidenceMatrix` used for duplicate pruning and parent inference.

## Important APIs, Types, and Functions

`BuildCoincidenceMatrix(root fs.FS, list []*Subsystem, excludeRe *regexp.Regexp)` is the public entry point. `matrixDebugInfo` stores matched file lists by subsystem. `includePathRe` limits scanned files to paths ending in `/` or `.c`, `.h`, or `.S`. `extractSubsystems` starts worker goroutines that apply a `subsystem.PathMatcher` to paths and emit `extracted` records.

## Control Flow

`BuildCoincidenceMatrix` creates a matcher, starts matcher workers and one result consumer, then walks the filesystem with `fs.WalkDir`. Directories and excluded paths are skipped; included files are sent to workers. The consumer records every matched subsystem set into the matrix and appends the path to debug file lists for each subsystem. After the walk, paths are closed, the consumer is awaited, and each debug file list is sorted for deterministic output.

## State, Dependencies, Risks, and Test Signals

State is local except for the returned matrix and debug info. Matching is concurrent, but matrix writes are serialized in the consumer goroutine. Dependencies include `io/fs`, `regexp`, `runtime.NumCPU`, `slices`, `sync.WaitGroup.Go`, and `subsystem.PathMatcher`. Risks include blocking if the walk exits early before closing paths, reliance on newer Go `WaitGroup.Go`, exclusion regex breadth, source-extension filtering that ignores generated or config files, and pointer-identity keys. Tests cover filtered `.git` paths, source-file counts, and pair counts.
