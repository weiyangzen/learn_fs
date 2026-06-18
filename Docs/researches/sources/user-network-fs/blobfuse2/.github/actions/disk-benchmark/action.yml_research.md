# sources/user-network-fs/blobfuse2/.github/actions/disk-benchmark/action.yml

Purpose: This composite GitHub Action benchmarks local disk read and write throughput with FIO and publishes results to GitHub Pages through `benchmark-action/github-action-benchmark`.

Important APIs, types, and functions: Inputs are required `GITHUB_TOKEN` and `ARCH`. The first step runs shell commands to create `/mnt/localssd` and `disk`, run sequential write and read FIO jobs, transform JSON output with `jq` into benchmark JSON files, remove the temporary FIO file, and print results. The next two steps publish write and read results separately with `tool: customBiggerIsBetter`, `auto-push: true`, branch `benchmarks`, and paths under `${{ inputs.ARCH }}/disk/write` and `${{ inputs.ARCH }}/disk/read`.

Control flow: The shell step uses `set -euo pipefail`, so FIO/JQ failures stop the action. Write benchmark creates `/mnt/localssd/fiotest.tmp`; read benchmark reads the same file; cleanup removes it. Publishing steps consume `disk/write.json` and `disk/read.json`.

State and persistence behavior: Runner-local state includes `/mnt/localssd/fiotest.tmp` and `./disk/*.json`. Persistent remote state is benchmark data pushed to the `benchmarks` branch by the benchmark action.

Dependencies and integration points: Requires `sudo`, `fio`, `jq`, writable `/mnt/localssd`, GitHub token permissions, and `benchmark-action/github-action-benchmark@v1`. It is intended for BlobFuse2 CI benchmark workflows and groups results by architecture.

Risks: The action assumes `/mnt/localssd` exists or can be used after `mkdir`, but it does not mount a disk there. `sudo chmod 777` is broad. `sudo mkdir disk` creates a workspace directory as root and then chmods it, which can be surprising. The read job depends on the write job leaving a valid 4 GiB file. `auto-push: true` mutates the `benchmarks` branch from CI and can fail on token/branch protection issues.

Test signals: There is no test file here; validation is by successful CI execution and generated benchmark history. The JSON conversion reports MiB/s by dividing FIO KiB/s by 1024.
