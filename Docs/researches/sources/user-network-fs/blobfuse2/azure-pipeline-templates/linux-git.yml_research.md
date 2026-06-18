# sources/user-network-fs/blobfuse2/azure-pipeline-templates/linux-git.yml

## Purpose
This template stress-tests Blobfuse2 by downloading, extracting, building Linux source, and cloning large Git repositories on the mount.

## Important APIs, Types, and Functions
It installs Linux build dependencies, generates file-cache or block-cache configs, mounts with `--file-cache-timeout=3200 --block-cache-pool-size=2048`, downloads Linux 6.13 tarball, runs `unxz`, `tar`, `make defconfig`, `make -j$(nproc)`, `make clean`, and clones VS Code, libfuse, and Azure Storage Fuse repositories.

## Control Flow
After installing tools and generating the selected cache config, it mounts Blobfuse2, prints mount contents, downloads and expands Linux source directly on the mount, builds and rebuilds it, then performs several Git clone operations under the mount.

## State and Persistence Behavior
It writes very large source trees and Git repositories into the mounted container and uses local cache storage. Cleanup is done by the calling nightly stage.

## Dependencies and Integration Points
It is optionally invoked by nightly `CompileLinux_GitClone` when `linux_git_test` is not `none`. It depends on internet access to kernel.org and GitHub plus build tool availability.

## Risks and Edge Cases
The test is bandwidth, CPU, and storage intensive. It downloads a fixed Linux version but labels it "latest". External network availability can fail the pipeline independent of Blobfuse2. Large builds can expose cache pressure and timeout issues.

## Test Signals
Signals include successful tar extraction, two successful kernel builds, successful `make clean`, and completed Git clones without filesystem errors.
