# sources/user-network-fs/blobfuse2/azure-pipeline-templates/verify-auth.yml

## Purpose
This template performs a lightweight mount-and-file-operations check for an authentication configuration.

## Important APIs, Types, and Functions
It accepts `idstring`, `distro_name`, and a step-valued `mountStep`. It uses `mount.yml` and then basic shell file operations on `$(MOUNT_DIR)`.

## Control Flow
The template mounts via the supplied mount step, prints `df`, Blobfuse2 processes, and a mount listing, then removes existing mount contents, creates directory `A`, creates/copies small files, lists the resulting tree, removes `A`, prints `blobfuse2-logs.txt`, and clears the log file.

## State and Persistence Behavior
It writes small files into the mounted test container, deletes the test directory, and clears local Blobfuse2 logs. It does not unmount or delete containers itself.

## Dependencies and Integration Points
It is used by proxy and MSI portions of the nightly pipeline to validate SAS/MSI auth configs without running the full E2E suite.

## Risks and Edge Cases
The check is intentionally shallow and may not catch auth edge cases beyond mount and simple IO. The listing, fileops, and remove steps all use `continueOnError: true`, so caller-level result handling is important. It depends on the supplied mount step already using the intended credential config.

## Test Signals
Signals are successful mount, file create/write/copy/list/remove operations, and no authentication errors in Blobfuse2 logs.
