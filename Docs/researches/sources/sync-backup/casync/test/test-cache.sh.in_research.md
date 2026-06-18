# sources/sync-backup/casync/test/test-cache.sh.in

Purpose: integration test for cache/store behavior.

Important APIs/types/functions: configured shell script drives the built `casync` binary against scratch directories, cache paths, and generated archives/indexes.

Control flow/state: creates a temporary workspace, runs make/extract/cache operations, compares expected outputs, and removes scratch state.

Dependencies/integration: relies on top build/source substitutions, compressor/digest defaults, and standard shell tools.

Risks/test signals: validates end-to-end cache reuse but can be sensitive to filesystem permissions and cleanup failures. Nonzero diff or command failure is the main oracle.

Source research group: `subset-b-009122`.
