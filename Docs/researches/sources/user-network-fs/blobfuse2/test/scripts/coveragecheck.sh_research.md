<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh -->
# sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh

Source path: `sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh`

## Purpose
Developer utility for coverage gating or dependency graph inspection.

## Important APIs, Types, And Functions
Shell functions: `overall_check`, `file_check`. Key variables: none declared. External commands observed: none declared.

## Control Flow
`coveragecheck.sh` parses coverage reports and fails when overall coverage is below 80% or per-file coverage below 70%. `depends.sh` builds `go mod graph` output and recursively prints reverse dependency sources for a requested module.

## State And Persistence
Reads generated coverage or Go module graph files and writes temporary graph files.

## Dependencies And Integration Points
Integrates with blobfuse/blobfuse2 CLI mount lifecycle, FUSE unmount tools, GNU coreutils, benchmark tools, Azure/MLPerf/Oracle environments where applicable, and result files consumed by manual or CI performance analysis.

## Risks
Parsing is format-sensitive and uses shell arithmetic/string processing that can fail on unexpected report values.

## Test Signals
Useful signals include command exit codes, generated result tables/logs, successful mount/unmount cycles, throughput or benchmark metrics, checksum comparisons, and absence of residual mount/temp data after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/coveragecheck.sh -->
