<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go

Purpose: benchmark negative lookup/stat performance through a FUSE directory that always returns ENOENT.

Important APIs, types, and functions: `benchLookupDir.Lookup` implements `fs.NodeRequestLookuper`; `doBenchLookup` runs repeated `os.Stat`; `benchLookupHelper` exposes it through HTTP JSON.

Control flow: benchmark mounts the filesystem, spawns the helper, builds a non-existent path, resets the timer, and asks the helper to stat it `b.N` times.

State and persistence behavior: no filesystem state beyond the mounted directory; all lookups are negative.

Dependencies and integration points: integrates fs lookup interfaces, fstestutil, spawntest, and HTTP JSON.

Risks and test signals: kernel negative dentry caching can affect results depending on FUSE entry validity behavior. Signal is stable benchmark timing and expected `os.IsNotExist` errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_lookup_test.go -->
