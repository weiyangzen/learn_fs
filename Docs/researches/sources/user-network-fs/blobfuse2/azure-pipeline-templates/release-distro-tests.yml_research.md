# sources/user-network-fs/blobfuse2/azure-pipeline-templates/release-distro-tests.yml

## Purpose
This template validates an installed Blobfuse2 release package on block blob and ADLS accounts by generating configs, mounting, and running quick E2E tests.

## Important APIs, Types, and Functions
Parameters include root/work/mount/temp directories, container, and extra mount flags. It calls installed `blobfuse2 version`, `blobfuse2 --help`, `blobfuse2 gen-test-config`, `blobfuse2 mount/unmount`, and `Go@0 test` under `test/e2e_tests`.

## Control Flow
It checks version/help, prepares mount and temp directories, generates a block config using block account variables, mounts block blob, verifies mount with `df`, runs quick E2E tests, unmounts and clears logs, then repeats config generation, mount, verify, E2E, and unmount for ADLS.

## State and Persistence Behavior
It writes block and ADLS config files under the root directory, uses the installed system `blobfuse2`, and writes test data into the provided container. Logs are printed and cleared.

## Dependencies and Integration Points
It is intended for release distro validation where Blobfuse2 has already been installed from a package. It depends on repository test code and Azure account variables.

## Risks and Edge Cases
It prints configs containing credentials unless masking catches them. It kills Blobfuse2 before mounting. The Go tests rely on source checkout even though the binary is system-installed.

## Test Signals
Signals include installed binary version/help output, successful block and ADLS mounts, and quick E2E pass for both account types.
