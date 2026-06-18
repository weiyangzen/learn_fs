# sources/user-network-fs/blobfuse2/azure-pipeline-templates/fio-data-integrity.yml

## Purpose
This template runs FIO workloads on a Blobfuse2 mount to validate data integrity across large sequential, random, multithreaded, and sparse-file cases.

## Important APIs, Types, and Functions
It generates file-cache or block-cache configs, mounts through `mount.yml`, installs `fio`, and executes job files under `test/fio/` including `rw.fio`, `seq-write-1f-10th.fio`, `hole_inside_blocks.fio`, and `hole_over_blocks.fio`.

## Control Flow
After config generation and mount, it clears the mount directory before each workload, then runs read/write 10G single-file, 1G x 10 files, random write variants, multithreaded offset writes, and sparse-hole workloads. Failure paths publish logs and traces.

## State and Persistence Behavior
It writes large FIO test data into the mounted Azure container, uses local cache paths, and emits `blobfuse2-logs.txt`/trace diagnostics on failure.

## Dependencies and Integration Points
It is optionally invoked by the nightly `FioTests` stage for file cache and block cache. It depends on FIO job files and adequate storage capacity/time.

## Risks and Edge Cases
The workloads are heavy and can be expensive or timeout-prone. Repeated `rm -rf ./*` depends on working directory being the mount. Validation relies on FIO job integrity settings in the job files, as noted by the file comments.

## Test Signals
Signals are successful FIO exits for all job files, no integrity mismatch, and useful log/trace output on failure.
