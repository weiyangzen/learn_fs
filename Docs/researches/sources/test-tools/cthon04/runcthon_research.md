# sources/test-tools/cthon04/runcthon

## Purpose
`runcthon` is a Bash orchestration script for running the Connectathon basic/general/special/lock tests against many NFS mount permutations. It mounts per-version/per-protocol directories, launches `./server` test runs in the background, captures logs under `/tmp`, waits between batches, and provides helper modes to create server-side directories or unmount prior runs.

## Important APIs, Types, and Functions
Important shell functions are `runtests()`, `umountall()`, and `mkdirs()`. Configuration variables include `SRV`, `serverdir`, `privatemnts`, `noudp`, `dokrb5`, `onlykrb5`, `nov4`, `dov41`, `dov42`, `nov2`, `onlyv3`, `onlyv4`, `minver`, `fsc`, `rdma`, `rdmaif`, `onlyrdma`, `nolcks`, and `port`.

## Control Flow and State
Option parsing sets feature flags, then loops over test letters `b g s l` unless locks are disabled. For each selected test it builds `mount` options for NFSv2/v3/v4/v4.1/v4.2, UDP/TCP/RDMA, optional Kerberos flavors, cachefiles (`fsc`), minor-version selection, and custom ports. Each invocation creates a mountpoint, runs `./server` in a subshell, logs failure output, unmounts if still mounted, and backgrounds the run before a batch `wait`.

## Persistence and Dependencies
State persists in created `/mnt` or `/mnt/<server>` mount directories, server-side `nfsv*` export directories, `/tmp/nfsv*` logs, live NFS mounts, and background `server` processes. Dependencies: Bash, `/proc/mounts`, `sudo umount`, `grep`, `awk`, `date`, `pkill`, local `./server`, NFS client mount options, RDMA port 20049 conventions, and external server export setup.

## Integration Points, Risks, and Test Signals
Integration is the highest-level Cthon launcher. Risks include unquoted variables, broad `pkill runcthon`/`pkill server` traps, a likely typo in `mkdirs()` using `$proto` while constructing `protos` for RDMA, racey log names, and root/sudo/mount privileges. Test signals are `Done` timestamps after each batch, absence of `.error` logs, no lingering `/proc/mounts` entries, and successful runs for every enabled protocol/security tuple.
