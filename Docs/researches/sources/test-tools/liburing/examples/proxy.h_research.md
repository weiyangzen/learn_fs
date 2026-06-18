# sources/test-tools/liburing/examples/proxy.h

## sources/test-tools/liburing/examples/proxy.h

Purpose: Shared helper header for `proxy.c` containing compact CQE/SQE user-data encoding and elapsed-time helpers.

Important APIs/types/functions: `struct userdata` union packs 4-bit op, 12-bit thread id, 16-bit buffer id, and 16-bit fd into a 64-bit value. `__encode_userdata`, `__raw_encode`, `cqe_to_op`, `cqe_to_bid`, `cqe_to_fd`, `mtime_since`, and `mtime_since_now`.

Control flow: inline pack/unpack functions are called when preparing SQEs and handling CQEs. Time helpers compute millisecond deltas with microsecond borrow handling.

State and persistence: none; pure encoding/time helpers.

Dependencies/integration: requires liburing types to be visible before inclusion. Used by proxy event dispatch and statistics.

Risks: fd and bid are truncated to 16 bits, op/tid share 16 bits with tid capped at 4095 even though proxy uses 1024. No endian issue inside a process, but bitfield layout in a union is compiler/ABI-sensitive; code is intended for local use, not serialization.

Test signals: proxy runtime dispatch correctness; bad user-data errors would reveal encoding mismatches.
