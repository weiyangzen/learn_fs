# sources/object-store/minio-mc/cmd/difference_test.go

Purpose: Tests exclude-pattern matching behavior used by difference/mirror style workflows.

Important APIs/types/functions: `testCases` and `TestExcludeOptions`.

Control flow: The table enumerates object storage and filesystem path suffixes, patterns, and expected booleans, then calls `matchExcludeOptions`.

State and persistence: No state or I/O.

Dependencies/integration: Depends on `matchExcludeOptions` and `ClientURLType` definitions outside this subset.

Risks: Despite the filename, it does not test the core `difference` merge/comparison logic, active-active modtime handling, metadata equality, error propagation, or Unicode normalization.

Test signals: Useful narrow signal for exclude pattern matching across object-storage and filesystem path styles.
