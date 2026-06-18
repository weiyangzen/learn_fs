<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py

## Purpose
Creates multiple 20GB zero-filled files in parallel on a target folder and reports aggregate create/write throughput.

## Important APIs, Types, and Functions
`create_file(file_index, folder)` builds a timestamped filename and runs `dd if=/dev/zero bs=16M count=1280 oflag=direct`. `main(folder, num_files)` ensures the folder exists, runs work through a `ThreadPoolExecutor` sized to CPU count, and prints a JSON record.

## Control Flow and State
Each worker uses an external `dd` process and records elapsed time. The parent computes total time and total data as `num_files * 20` GB. Files are left in the target folder.

## Dependencies and Integration Points
Depends on Python standard libraries plus Unix `dd`. Intended for mounted Blobfuse2 paths or local disks under performance testing.

## Risks and Edge Cases
`subprocess.run(..., shell=True)` uses interpolated paths and is unsafe for untrusted folder names. Return codes are ignored, so failed `dd` processes still contribute to reported throughput. `oflag=direct` may fail depending on filesystem alignment/support. The JSON name says `create_10_20GB_file` regardless of `num_files`.

## Test Signals
Single JSON line reports total time, speed, and unit. It does not validate file sizes or failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/highspeed_create.py -->
