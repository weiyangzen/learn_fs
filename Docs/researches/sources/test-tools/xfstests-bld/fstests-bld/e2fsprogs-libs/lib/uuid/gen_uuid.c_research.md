# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid.c

## Purpose
`gen_uuid.c` implements portable DCE-compatible UUID generation for random UUIDs, time-based UUIDs, and an automatic front end that chooses the best available source.

## Important APIs, Types, and Functions
Public functions are `uuid__generate_time()`, `uuid_generate_time()`, `uuid__generate_random()`, `uuid_generate_random()`, and `uuid_generate()`. Core helpers include `get_random_fd()`, `get_random_bytes()`, `get_node_id()`, `get_clock()`, `read_all()`, `close_all_fds()`, and `get_uuid_via_daemon()`.

## Control Flow
Random generation prefers `/dev/urandom` or nonblocking `/dev/random`, then mixes libc PRNG and optional thread-id `jrand48` data, and sets version/variant bits. Time generation tries `uuidd` for serialized or bulk UUIDs, otherwise discovers a hardware node id or random multicast node, obtains a locked timestamp/clock sequence from `/var/lib/libuuid/clock.txt`, sets version/variant fields, and packs the UUID.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes static random fd, PRNG seeds, cached node id, thread-local clock adjustment/last timestamp/state fd, and persisted clock sequence file. Dependencies include Unix random devices, network interface ioctls, fcntl locks, optional Unix-domain uuidd, fork/exec, syscalls, and `uuid_pack`/`uuid_unpack`. Risks include fallback entropy quality, clock file permission/locking failures, static state races without TLS, daemon startup assumptions, and platform-specific network MAC discovery. Test signals include version 1 and version 4 bit layout, uniqueness under rapid generation, behavior without `/dev/urandom`, uuidd bulk path, and `tst_uuid`.
