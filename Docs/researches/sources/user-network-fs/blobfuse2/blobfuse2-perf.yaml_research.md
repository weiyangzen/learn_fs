# sources/user-network-fs/blobfuse2/blobfuse2-perf.yaml

## Purpose
This weekly Azure DevOps performance pipeline compares Blobfuse2 cache modes, Blobfuse v1 behavior, FIO workloads, upload/download, Git clone performance, and optionally ResNet50 image classification throughput.

## Important APIs, Types, and Functions
It schedules weekly Saturday runs, has parameter `resnet_test`, uses `build.yml` and `cleanup.yml`, generates Blobfuse2 and Blobfuse v1 configs, and invokes scripts `test/scripts/file_block_compare.sh`, `fio.sh`, `run.sh`, `git_clone.sh`, `test/perf_test/resnet50_classify.py`, and `test/perf_test/generate_perf_report.py`.

## Control Flow
The `ShortRunning` stage runs on the perf pool, installs libraries and Blobfuse v1, cleans the workspace, clones the repo manually, checks out the pipeline branch, builds Blobfuse2, generates v2 file/block configs and v1 config, runs block-vs-file compare, sequential/random/CSI FIO tests, upload/download tests, and Git clone tests, printing result files after each. If enabled, `LongRunning` installs Python ML dependencies, compares an older Blobfuse2 release package with the current main build on ResNet50, generates a performance report, publishes the JSON artifact, unmounts, and cleans up.

## State and Persistence Behavior
It uses fixed paths under `/home/vsts/workv2` and `/mnt/blobfuse2tmp`, writes performance result files in the repo workspace, writes `blobfuse2-perf.json`, mounts/unmounts storage, and publishes the performance JSON artifact.

## Dependencies and Integration Points
It depends on a dedicated `blobfuse-perf-pool`, performance storage account variables, internet access for repo clone and old release download, Blobfuse v1 apt package, FIO, Python/TensorFlow/Pillow for ResNet, and repository perf scripts.

## Risks and Edge Cases
Performance jobs are highly sensitive to self-hosted runner drift, network conditions, and fixed workspace paths. The template passes parameter names to `build.yml` that do not match its current parameter contract, suggesting legacy drift. It clones from GitHub rather than using checkout, so branch resolution must work from `Build.SourceBranch`.

## Test Signals
Signals include populated result text files, successful FIO/upload/download/git clone scripts, published `Blobfuse2_performance_report`, and regression script pass for ResNet metrics.
