# sources/user-network-fs/go-fuse/fs/maxwrite_test.go

Purpose: Linux test for mount `MaxWrite`, `MaxReadAhead`, and `max_read` effects on observed kernel request sizes.

Important types/functions: `maxWriteTestRoot` records largest read/write sizes; `maxWriteTestNode` reports a 1 GiB file and returns `maxWriteTestFH`; the file handle records request sizes in `Read`/`Write`. `TestMaxWrite` iterates many mount option combinations, verifies `/sys/class/bdi/.../read_ahead_kb`, performs 2 MiB direct and buffered I/O, and checks observed sizes against kernel capabilities. `bdiReadahead` reads sysfs.

State/dependencies: Linux-only, real FUSE mount, O_DIRECT, sysfs, kernel capability flags.

Risks/test signals: valuable kernel negotiation coverage but environment-sensitive. It accounts for pre-4.20 lack of `CAP_MAX_PAGES`.
