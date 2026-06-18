<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh -->
# sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh

## Purpose
AI workload benchmark harness for loading/saving model checkpoints through Blobfuse2 using preload, file-cache, and block-cache modes across CPU/CUDA configurations.

## Important APIs, Types, and Functions
`clear_cache` removes Hugging Face caches and drops kernel caches. The `models`, `fusemode`, and `devices` arrays define the matrix. In `model` mode, it downloads models via `load.py` and saves checkpoints to `/mnt/model`. In benchmark mode, it mounts a subdirectory with `./blobfuse2`, optionally parses preload progress from logs, then invokes `python3 load.py --checkpoint_path`.

## Control Flow and State
The script writes `stats.log`, mutates `/mnt/blobfuse/checkpoint`, `/mnt/cpramdisk`, `/mnt/hugging_cache`, mounts/unmounts Blobfuse2 and tmpfs, clears caches, and loops across all device/cache/model combinations.

## Dependencies and Integration Points
Requires Blobfuse2 binary, Azure MSI auth, large Azure container data, Hugging Face/transformers/torch stack, GPUs for CUDA modes, sudo, tmpfs capacity, and `bc`.

## Risks and Edge Cases
Hard-coded storage account/container and local mount paths make it environment-specific. It can allocate a 600G tmpfs and delete cache directories. `mcuda` requires multi-GPU support. Many commands are unquoted and the script lacks strict error mode.

## Test Signals
`stats.log` records model load/save times, checkpoint sizes, bandwidth, preload summaries, and mount failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/checkpointLoad.sh -->
