# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/634

## Purpose
This fixture validates a KMSAN kernel info leak reported in `urandom_read_nowarn`.

## Important APIs, types, and functions
Important frames include `_copy_to_user`, `urandom_read_nowarn`, `__x64_sys_getrandom`, `chacha_permute`, `chacha_block_generic`, `_extract_crng`, `_get_random_bytes`, `get_random_bytes`, `nsim_dev_trap_report_work`, and worker-thread frames.

## Control flow
Uninitialized bytes originate in CRNG/chacha reseed and extraction paths, then are copied to userspace by `getrandom` through `urandom_read_nowarn`.

## State and persistence behavior
The fixture persists origin stacks, byte count, kernel address, and user destination address for the info leak.

## Dependencies and integration points
It tests KMSAN info-leak parsing, random-number generator stacks, and copy-to-user sink handling.

## Risks and test signals
The parser must use `urandom_read_nowarn` rather than `_copy_to_user` as the title frame and classify the type as `KMSAN-INFO-LEAK`.
