# File Research: sources/virtualization/nbdkit/plugins/rust/examples/ramdisk.rs

Example Rust nbdkit plugin implementing an in-memory RAM disk. Global mutex-protected state tracks the configured disk size, backing `Vec<u8>`, and whether writes should emit debug hexdumps.

The `Server` implementation supports `size=` and `hexdump=` configuration, allocates the disk in `get_ready`, logs readonly/TLS status in `open`, returns disk size, and implements locked reads/writes into the shared vector. It opts into `ThreadModel::Parallel` but serializes backing storage access through mutexes, then registers `thread_model`, `write_at`, `config`, and `get_ready` with `plugin!`.
