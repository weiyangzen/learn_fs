<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh

## Purpose
Provisions a VM for read-cache fio experiments, including local SSD RAID, fio from source, Go, gcsfuse, and helper aliases.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Creates RAID0 over four local NVMe SSDs if needed, installs fio 3.36 from source with a percentile-range patch, clones gcsfuse, installs Go from `.go-version`, installs gcsfuse from master, mounts the benchmark bucket, and appends env/aliases to bashrc.

## State And Persistence Behavior
Formats and mounts `/dev/md0`, writes `$HOME/working_dir`, mutates `~/.bashrc`, installs system packages, and installs Go/gcsfuse binaries.

## Dependencies
Depends on four Google local SSD devices, mdadm, apt, git, Go downloads, fio source, and GitHub access.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Very destructive if local SSD assumptions are wrong; installs gcsfuse from `master` rather than the checked-out source under test.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh -->
