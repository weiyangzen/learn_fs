<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg

## Purpose
FIO configuration for a 15GB random-read benchmark against a Blobfuse2-mounted file.

## Important APIs, Types, and Functions
`[global]` sets `ioengine=sync`, `size=15G`, `bs=16M`, `rw=randread`, `filename=/usr/blob_mnt/testFile15GB`, and `numjobs=20`. `[job]` names the job `seq_read`, despite random-read mode.

## Control Flow and State
FIO uses this config to perform read workload against the configured file. It does not create repository state but reads or may prepare workload state depending on FIO behavior and file existence.

## Dependencies and Integration Points
Requires `fio` and a mounted path containing or able to create `/usr/blob_mnt/testFile15GB`.

## Risks and Edge Cases
The job name conflicts with `rw=randread`, which can confuse reports. Hard-coded filename limits portability. `numjobs=20` can stress client and storage account heavily.

## Test Signals
FIO output provides throughput, IOPS, and latency metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/fio.cfg -->
