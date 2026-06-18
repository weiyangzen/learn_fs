# sources/user-network-fs/mergerfs/tests/tests.cpp

## Purpose

This file is the main acutest-based C++ unit and stress test harness for several mergerfs support libraries. It is not focused on one FUSE operation; it validates low-level behavior that the filesystem runtime depends on: configuration value parsing, branch list mutation semantics, inode calculation, string and numeric helpers, random utilities, thread-pool scheduling, copyfile behavior, hash-set de-duplication, and rmdir error aggregation.

The test list at the bottom registers every test with acutest through `TEST_LIST`. That registration makes this file the integration point between the build/test runner and the support modules included from `config.hpp`, `fs_copyfile.hpp`, `fs_inode.hpp`, `from_string.hpp`, `hashset.hpp`, `num.hpp`, `rnd.hpp`, `str.hpp`, `thread_pool.hpp`, and vendored `rapidhash/rapidhash.h`.

## Important APIs, types, and functions

`wait_until` is a small polling helper for asynchronous tests. It repeatedly evaluates a predicate for up to a millisecond-based timeout and is used in thread-pool tests where work execution, queue pressure, or resizer threads need deterministic completion signals without fixed long sleeps.

The config tests exercise `ConfigBOOL`, `ConfigU64`, `ConfigINT`, `ConfigSTR`, `CacheFiles`, `InodeCalc`, `MoveOnENOSPC`, `NFSOpenHack`, `StatFS`, `StatFSIgnore`, `XAttr`, and the aggregate `Config` registry. The tested API shape is consistently `from_string`, `to_string`, comparison operators, `Config::set`, `Config::get`, `Config::has_key`, `Config::get_map`, `Config::from_stream`, `Config::from_file`, `Config::finish_initializing`, xattr-list helpers, and static recognizers/pruners for control and command xattrs.

The branch tests cover `Branch`, `Branches`, `Branches::Impl`, and `SrcMounts`. They validate branch modes `RW`, `RO`, and `NC`; per-branch and global `minfreespace`; copy and move behavior; copy-on-write snapshots through `Branches::Ptr`; string serialization; instruction prefixes for set/add/erase; fnmatch-based deletion; and path parsing where `=` may appear in the path and the last `=` is the option separator.

The inode tests use `fs::inode::set_algo`, `fs::inode::get_algo`, `fs::inode::calc`, and `fs::inode::ReaddirCalc`. The tested algorithms are `passthrough`, `path-hash`, `path-hash32`, `devino-hash`, `devino-hash32`, `hybrid-hash`, and `hybrid-hash32`.

The thread-pool tests exercise `ThreadPool` construction, `ptoken`, `enqueue_work`, token-aware enqueue, `try_enqueue_work`, `try_enqueue_work_for`, `enqueue_task`, `threads`, `add_thread`, `remove_thread`, and `set_threads`. They use `std::atomic`, `std::future`, producer threads, queue saturation, and repeated resize/churn scenarios to validate concurrency behavior.

Other targeted APIs include `fs::copyfile`, `HashSet::put`, `HashSet::size`, `str::split`, `split_to_set`, `split_on_null`, `lsplit1`, `rsplit1`, `splitkv`, `join`, prefix/suffix helpers, trimming, replacement, fnmatch erasure, `str::from` numeric parsing, `num::humanize`, `RND::rand64`, `RND::shrink_to_rand_elem`, and `rapidhash_withSeed`/`rapidhashNano_withSeed`/`rapidhashMicro_withSeed`.

`RmdirErr` is a local test replica of rmdir error-reduction behavior. It stores the first result in an `std::optional<int>`, defaults to `-ENOENT` if no branch returned a result, gives `-EEXIST` and `-ENOTEMPTY` priority, lets success replace generic errors, and prevents generic errors or success from overwriting priority errors.

## Control flow

The file is organized as independent `void test_*()` functions. Most tests construct a small object, mutate it through its public API, and assert exact return codes and serialized values with `TEST_CHECK`. The test runner invokes registered functions from `TEST_LIST`.

Configuration control flow is primarily round-trip oriented: parse a string, assert internal enum/value state through equality or getters, serialize back, and assert invalid inputs return negative errno values such as `-EINVAL`, `-EOVERFLOW`, `-ENOATTR`, `-EROFS`, or `-ERANGE`. `Config::from_stream` tests demonstrate partial progress: valid lines are applied even when a bad key causes an overall error and records diagnostics in `cfg.errs`.

Branch mutation tests model an instruction language. A bare string or `=` replaces the branch list, `+` and `+>` append, `+<` prepends, `->` removes the last branch, `-<` removes the first branch, and `-pattern` removes fnmatch matches. Several tests explicitly verify atomic failure: if one path in a multi-path add or set is invalid, the previous branch list remains unchanged.

Thread-pool control flow ranges from simple enqueue-and-wait tests to stress tests with concurrent producers and resizers. Queue backpressure tests deliberately occupy the only worker and fill a depth-one queue, then assert non-blocking enqueue fails, timed enqueue times out, and blocking enqueue waits until a slot opens. Destructor behavior is covered by queuing work inside a scope and asserting all queued work completed after the pool is destroyed.

`fs::copyfile` tests create temporary directories under `/tmp`, open source files with POSIX APIs, write sparse endpoints, call `fs::copyfile`, then verify size and boundary bytes. The mutation test updates source timestamps concurrently during copy and then checks that cleanup removed temporary destination-prefixed files.

## State and persistence behavior

Most tests are in-memory, but they cover state that controls live filesystem behavior. `Config` owns a map of mutable/readonly runtime options; tests verify key normalization between underscores and hyphens for `get`/`set`, readonly enforcement before and after initialization, alias behavior for remember/noforget options through global `fuse_cfg.remember_nodes`, and xattr-form key enumeration as NUL-separated `user.mergerfs.*` strings.

`Branches` state is copy-on-write through pointer snapshots. Tests ensure each mutation produces a new implementation pointer while old snapshots remain unchanged. The most sensitive persistence-like behavior is the relation between a branch's `_minfreespace` variant and the containing `Branches::Impl` default: copy and move assignment must relink pointer-backed branch defaults to the destination impl's default, not leave dangling or cross-linked pointers.

Thread-pool tests validate live concurrent state: worker count, queue occupancy, producer tokens, futures, resize operations, exception handling, and destructor draining. These tests are important because regressions can produce hangs rather than clean assertion failures.

Filesystem state appears in the copyfile tests only. Temporary files are created with `mkdtemp`, source files are truncated and written, destinations are inspected with `stat`/`pread`, and all test directories are removed with `std::filesystem::remove_all`. The cleanup test also treats leftover hidden temporary files as a failure signal.

## Dependencies and integration points

The file integrates with the acutest framework through `acutest/acutest.h` and `TEST_LIST`. It depends on mergerfs internal headers for configuration, inode, string, numeric, random, hash-set, copyfile, and thread-pool behavior. It also uses POSIX headers and syscalls (`open`, `ftruncate`, `pwrite`, `pread`, `stat`, `fstat`, `utimensat`, `mkdtemp`, `close`) plus C++ standard library concurrency, filesystem, stream, and container facilities.

The config tests are directly tied to runtime control surfaces: config file parsing, runtime xattrs, mutable and readonly mount options, branch lists, and FUSE node-remember behavior. The inode tests connect to directory listing and stable inode reporting. The thread-pool tests connect to any mergerfs subsystem using pooled work, especially where runtime resizing is exposed through configuration. The copyfile tests connect to clone/copy fallback behavior used when moving or materializing data across branches.

## Risks and edge cases

Branch parsing is a high-risk area. The tests document strict uppercase mode parsing, byte/K/M/G/T suffix behavior, rejection of negative and overflowing minfreespace, support for lowercase size suffixes, preservation of paths containing `=`, atomic failure semantics, and the fact that empty string and `=` both clear the list.

Global and per-branch `minfreespace` ownership is subtle. Pointer-backed branches intentionally track a global default live, copied pointer-backed `Branch` instances share the pointer, and `Branches::Impl` assignment must relink default pointers. A regression here could corrupt runtime branch free-space policy or leave stale pointers.

Thread-pool tests expose deadlock and race risks: blocking enqueue under full queues, timed enqueue duration, exceptions from worker functions including non-`std::exception` throws, concurrent enqueue with resize, add/remove churn, destructor draining, FIFO ordering with one worker, and move-only callables passed through futures.

Config risks include alias drift, inconsistent underscore normalization, readonly enforcement mistakes, xattr buffer sizing and `-ERANGE` handling, partial config-file error reporting, and global `fuse_cfg` side effects. Tests restore `fuse_cfg.remember_nodes` after mutation, but failures before restoration would affect later tests.

File-copy tests rely on `/tmp`, sparse file support, timestamp mutation, and cleanup of temporary files. They can be more environment-sensitive than pure unit tests. Thread stress tests also use timing and may be sensitive on heavily loaded systems, though `wait_until` reduces fixed-sleep flakiness.

## Test signals

Primary signals are exact acutest assertions: return codes, serialized strings, enum equality, preserved values after invalid writes, expected errors for missing/unknown keys, exact thread counts, nonzero and unique worker ids, future values or propagated exceptions, queue-full failures, timeout lower bounds, total executed work counters, absence of leftover copy temporary files, hash-set duplicate return values, and deterministic hash equality against `rapidhash_internal`.

The breadth of `TEST_LIST` is itself a signal: if a new helper or option is added without registration, it will not run. The registered names also provide a useful map from failing test output back to a subsystem: `branches_*`, `config_*`, `tp_*`, `fs_inode_*`, `fs_copyfile_*`, `hashset_*`, `str_*`, `rnd_*`, and `rapidhash_*`.
