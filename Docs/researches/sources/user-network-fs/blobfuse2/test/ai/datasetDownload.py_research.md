<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py -->
# sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py

## Purpose
Benchmarks Hugging Face dataset loading and optional saving to disk.

## Important APIs, Types, and Functions
CLI args are `--data_path`, `--subset`, and `--dest_path`. It calls `datasets.load_dataset(data_path, subset, num_proc=25)`, prints load time, and optionally calls `dataset.save_to_disk(dest_path, num_proc=25)`.

## Control Flow and State
All work is top-level after argument parsing. It reads remote or local datasets and optionally writes a saved dataset directory.

## Dependencies and Integration Points
Depends on Hugging Face `datasets`. Used by AI data benchmark shell scripts against Blobfuse2-mounted or local paths.

## Risks and Edge Cases
Unused imports indicate script drift. `num_proc=25` can overuse CPU and may not fit every dataset. No exception handling or validation is present.

## Test Signals
Printed load/save durations indicate performance. Dataset correctness is not independently verified.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/datasetDownload.py -->
