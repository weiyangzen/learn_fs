# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd/eventfd04.c

Purpose: Verifies `select()` write readiness for eventfd descriptors below and at the maximum counter value.

Important APIs/types/functions: `eventfd`, `select()`, write fd sets, `SAFE_WRITE`, `SAFE_READ`, and the `UINT64_MAX - 1` eventfd saturation boundary.

Control flow: The test writes a small value and expects write readiness, drains that value, writes `UINT64_MAX - 1`, calls `select()` again with the descriptor in the write set, and expects it not to be writable.

State and persistence behavior: The eventfd counter is the relevant state: writable while another write can be accepted, not writable once the counter is saturated.

Dependencies and integration points: Runs as a single LTP test requiring `CONFIG_EVENTFD`; no persistent filesystem state is involved.

Risks and test signals: This is sensitive to exact eventfd readiness semantics and fdset mutation. A kernel that allows overflow-prone writes or misreports `POLLOUT` readiness would fail.
