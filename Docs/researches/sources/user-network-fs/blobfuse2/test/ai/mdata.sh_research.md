<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/mdata.sh -->
# sources/user-network-fs/blobfuse2/test/ai/mdata.sh

## Purpose
AI dataset benchmark driver that downloads datasets and measures loading them through different Blobfuse2 cache modes.

## Important APIs, Types, and Functions
Writes `stats.log`, invokes an external `data.sh` helper with modes such as `hugging`, `file-cache`, `block-cache`, `preload`, and `ramdisk`, then runs `datasetDownload.py` for Hugging Face datasets or mounted paths.

## Control Flow and State
The script first benchmarks remote Hugging Face loading for `cosmopedia` and `nvidia/OpenMathReasoning`, then iterates cache modes for each model/dataset name and appends timings to `stats.log`.

## Dependencies and Integration Points
Depends on sibling `datasetDownload.py`, an unlisted `data.sh`, Hugging Face datasets, and Blobfuse2 mounted paths prepared by the cache-mode helper.

## Risks and Edge Cases
The referenced `data.sh` is not in the assigned file list and may be missing. `datasetDownload.py` is called without `--dest_path`, so only load timing is captured. Hard-coded dataset names and mount path assumptions limit portability.

## Test Signals
`stats.log` with per-mode load timings is the primary output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/mdata.sh -->
