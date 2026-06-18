# sources/user-network-fs/blobfuse2/azure-pipeline-templates/huge-list-test.yml

## Purpose
This template validates listing behavior and request count on a pre-populated huge container, such as the `million-files` benchmark container.

## Important APIs, Types, and Functions
Parameters include `idstring`, a step-valued `mountStep`, and `distro_name`. It uses `fusermount`, `pidof`, `df`, `ls -1 | wc -l`, log grep for `OUTGOING REQUEST`, and log clearing.

## Control Flow
It pre-cleans stale mounts/processes, runs the supplied mount step, waits and verifies the mount, lists the mount root and counts entries, counts outgoing requests in `blobfuse2-logs.txt`, prints logs, clears logs, then unmounts without deleting container data.

## State and Persistence Behavior
It intentionally does not delete container data because the huge dataset is reused. It mutates only mount state and local logs.

## Dependencies and Integration Points
It is used by `verbose-tests.yml` after generating a config against `huge_container`. It depends on a pre-existing container with many entries.

## Risks and Edge Cases
If cleanup deletes mount contents accidentally, the shared huge dataset could be damaged, so this template avoids container cleanup. Listing can exceed timeout if the container size or service latency changes.

## Test Signals
Signals include successful root listing count, acceptable outgoing request count from logs, and clean unmount after the listing test.
