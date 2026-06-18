# File Research: sources/teaching/xv6-public/forktest.c

Small user-space process table exhaustion test.

Behavior:
- Provides a tiny local `printf` to keep the binary small.
- Forks up to 1000 children until `fork` fails.
- Children exit immediately.
- Parent waits for all children and verifies one extra `wait` returns `-1`.

Purpose:
- Tests graceful `fork` failure when process table capacity is exhausted.
