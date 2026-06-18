<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py -->
# sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py

## Purpose
Downloads a specific Kaggle dataset into a hard-coded Blobfuse2 mount path.

## Important APIs, Types, and Functions
Creates `kaggle.KaggleApi`, calls `authenticate`, then calls `dataset_download_files("miguelcalado/resnet50rafa", path="/mnt/blobfuse/mnt/resnet50rafa", unzip=True)`.

## Control Flow and State
All work executes at top level. It writes downloaded/unzipped dataset files into `/mnt/blobfuse/mnt/resnet50rafa`.

## Dependencies and Integration Points
Depends on Kaggle credentials, `kaggle` package, network access, and a mounted/writable `/mnt/blobfuse/mnt`. Several imported ML libraries are unused.

## Risks and Edge Cases
Hard-coded dataset and destination path make it non-general. It can consume significant disk/storage. No error handling or path creation exists.

## Test Signals
Kaggle download output and resulting files are the completion signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/ai/kaggle_download.py -->
