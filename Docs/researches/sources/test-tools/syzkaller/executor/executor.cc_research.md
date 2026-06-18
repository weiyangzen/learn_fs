# sources/test-tools/syzkaller/executor/executor.cc

Purpose: Main syzkaller executor binary. It implements command dispatch (`runner`, `exec`, `leak`, `test`), the child execution protocol, program decoding, syscall scheduling, coverage/comparison collection, and flatbuffer result construction.

Important APIs and control flow: `main` initializes OS state, maps input/output, sets control pipes, negotiates `handshake_req`, receives `execute_req`, opens coverage buffers, then enters the selected sandbox. `execute_one` decodes the varint program stream: copyin commands materialize constants, addresses, result references, data, and checksums; syscall commands are scheduled through `schedule_call`; copyouts are harvested in `copyout_call_results`. Threaded execution uses `thread_t` events, `worker_thread`, and per-call timeouts. Results are serialized through `write_output`, `write_call_output`, `write_extra_output`, and `finish_output`. `ShmemAllocator` and `ShmemBuilder` allow flatbuffers to be assembled directly inside shared memory.

State and persistence: global flags mirror RPC execution/environment options; `threads`, `results`, `extra_cov`, dedup tables, `output_data`, and optional `CoverFilter`s are reused across requests. With fork server enabled, output mappings are resized per request; snapshot mode reuses fixed ivshmem mappings.

Dependencies and integration: includes generated `syscalls.h`, `common.h`, OS-specific `executor_*.h`, `shmem.h`, `conn.h`, `files.h`, `snapshot.h`, `executor_runner.h`, and tests. It depends on flatrpc schemas and platform KCOV/KSANCOV/no-cover APIs.

Risks and tests: correctness hinges on shared-memory bounds, memory-ordering stores to `OutputData`, varint bounds checks, and matching constants with Go packages. Known risk areas include coverage buffer overflow/truncation, unfinished syscalls, thread-state races, and executor output corruption by fuzzed programs. `run_tests` covers checksum/copyin/filter/glob/KVM helpers; broader validation comes from syzkaller executor integration tests and machine checks.
