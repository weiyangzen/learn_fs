# sources/test-tools/fio/pshared.h

Purpose: declarations for process-shared pthread initialization helpers.

Important APIs/types: includes `<pthread.h>` and declares mutex, condition, and combined initialization helpers.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `pshared.c`; consumers pass caller-owned pthread objects.

Risks: API returns raw pthread error codes, not `errno`, so callers must handle that convention.

Test signals: compile and runtime initialization tests under relevant configure matrices.
