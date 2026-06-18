<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/load.py -->
# sources/user-network-fs/blobfuse2/test/ai/load.py

## Purpose
Loads Hugging Face causal language models or local checkpoints, optionally saves checkpoints, and reports load/save bandwidth based on checkpoint size.

## Important APIs, Types, and Functions
`get_directory_size` sums file sizes recursively. `load_model` loads tokenizer/model from a model name with optional cache path. `load_checkpoint` loads tokenizer/model from a checkpoint path, supporting `cpu`, `cuda`, or `mcuda` device modes. `save_checkpoint` writes model/tokenizer to a timestamped directory using safe serialization and configurable shard size. `main` parses CLI args and selects model or checkpoint flow.

## Control Flow and State
The script reads from Hugging Face Hub or local checkpoint paths, may write a timestamped checkpoint under `dest_path`, and prints timing, size, and bandwidth summaries. It moves models to the selected device or uses `device_map="auto"` for `mcuda`.

## Dependencies and Integration Points
Depends on `transformers`, PyTorch, and local/GPU resources. Used by `checkpointLoad.sh` and related Blobfuse2 AI workload tests.

## Risks and Edge Cases
`trust_remote_code=True` executes model repository code and is risky for untrusted models. Large models require substantial memory/GPU capacity. `cache_path` can be `None`. If neither `model_name` nor `checkpoint_path` is supplied, the script exits silently. Imported `DataParallel` is not used.

## Test Signals
Printed load/save timing, checkpoint size, and bandwidth are performance signals. Successful model/tokenizer object creation is the functional signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/load.py -->
