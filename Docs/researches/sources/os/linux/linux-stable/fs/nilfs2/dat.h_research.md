# File Research: sources/os/linux/linux-stable/fs/nilfs2/dat.h

## Summary
Declares the NILFS disk address translation API.

## Main Contents
- Virtual-to-physical translation.
- DAT allocation/start/end/update prepare, commit, and abort operations.
- Dirty marking, vector free, block move, virtual info export, and DAT read APIs.

## Important Details
The API exposes transactional triplets for allocation, ending, and update operations so bmap code can prepare all required metadata before committing structural changes.

## Risks
Callers must match prepare functions with the correct commit or abort function. Mixing old and new `nilfs_palloc_req` objects incorrectly can corrupt virtual block lifetime state.
