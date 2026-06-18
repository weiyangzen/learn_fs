# sources/user-network-fs/blobfuse2/.github/actions/perftesting/action.yml

## Purpose
This composite GitHub Action builds Blobfuse2 on a benchmark runner, creates a storage-backed mount configuration, runs FIO read/write benchmark scripts, and publishes bandwidth and latency JSON results to the `benchmarks` branch when running on `main`.

## Important APIs, Types, and Functions
The action input contract is `ARCH`, four Azure account/key pairs for standard, premium, standard HNS, and premium HNS accounts, `BENCH_CONTAINER`, `GITHUB_TOKEN`, and `CACHE_MODE`. It calls repository scripts `go_installer.sh`, `build.sh`, `tools/install_fio.sh`, `perf_testing/scripts/fio_bench.sh`, and `blobfuse2 gen-test-config`. It integrates with `benchmark-action/github-action-benchmark@v1` and the local `.github/actions/disk-benchmark` action.

## Control Flow
Steps install FUSE3 and tools, install Go, build Blobfuse2, copy the binary to `/usr/bin`, select `AZURE_STORAGE_ACCOUNT` and `AZURE_STORAGE_ACCESS_KEY` from `matrix.TestType`, generate either block-cache or file-cache config, optionally creates an ARM64 RAID0 local SSD mount, optionally runs disk benchmarks once, prepares mount/cache paths, then runs read and write FIO benchmark scripts. Result publishing is gated to `github.ref == refs/heads/main`.

## State and Persistence Behavior
The action mutates runner state by installing apt packages, killing apt locks, creating `/mnt/blob_mnt` and `/mnt/localssd/tempcache`, creating `/dev/md0` on ARM64, and exporting Azure credentials through `GITHUB_ENV`. Benchmark JSON is persisted to the `benchmarks` branch by the benchmark action.

## Dependencies and Integration Points
It is invoked by `.github/workflows/benchmark.yml` and assumes matrix keys `TestType` and `CacheMode` exist. It depends on self-hosted benchmark runners, Azure storage secrets, FUSE3, Go, FIO, jq, mdadm, and repository config templates `azure_block_bench.yaml` and `azure_key_perf.yaml`.

## Risks and Edge Cases
The YAML uses `if :` with a space before the colon in several steps, which is suspicious for GitHub Actions syntax. ARM64 disk setup assumes exactly six NVMe partition devices. Config files and logs print generated config contents, so secret redaction depends on GitHub masking. Apt lock killing is aggressive. Benchmark publication auto-pushes to a branch and can conflict with concurrent benchmark jobs.

## Test Signals
Useful signals are a manual `benchmark.yml` run, successful config generation for both cache modes, FIO script exit status, created `read/*_results.json` and `write/*_results.json`, benchmark branch updates, and ARM64 runner validation that `/mnt/localssd` exists before file-cache tests.
