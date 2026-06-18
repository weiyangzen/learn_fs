# sources/user-network-fs/blobfuse2/azure-pipeline-templates/data.yml

## Purpose
This helper template generates random local files, copies them into a Blobfuse2 mount through several copy methods, and validates mount content hashes against the local originals.

## Important APIs, Types, and Functions
Parameters are `generate_data`, `copy_data`, and `check_consistency`. It uses `dd`, `md5sum`, `cp`, `tar`, GNU `parallel`-style behavior in scripts, kernel cache dropping, and Azure DevOps variable `DATA_DIR`.

## Control Flow
When generating, it recreates `$(ROOT_DIR)/data_files`, emits `DATA_DIR`, and creates files across byte, KB, and MB block sizes and multiple counts. Copy mode writes those files to `$(MOUNT_DIR)` with regular copies and suffix variants for sequential, tar-parallel, and async/parallel paths. Check mode drops kernel page cache, computes hashes for original and copied variants, extracts hash columns, and diffs each mount hash list against the local checklist.

## State and Persistence Behavior
It persists generated files under `DATA_DIR`, temporary checksum files under the home directory, and copied data in the mounted Azure container. It clears old `~/mc*` files before verification.

## Dependencies and Integration Points
It is consumed by `data-integrity.yml` and depends on a mounted Blobfuse2 filesystem plus local data generation having run before copy/check phases.

## Risks and Edge Cases
Large random data generation is IO-heavy. Hash comparison assumes exact filename suffix conventions from copy steps. Dropping kernel cache requires sudo and affects the whole runner.

## Test Signals
Signals are successful creation of all file sizes, no copy errors, and zero diff between local checksum list and every mount checksum variant.
