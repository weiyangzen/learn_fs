# sources/test-tools/stress-ng/core-mounts.h

Purpose: exposes mount enumeration helpers.

Important APIs/types: declares `stress_mount_get(char *mnts[], int max)` and `stress_mount_free(char *mnts[], int n)`.

Control flow: no header flow; callers request up to `max` mount strings and later free the returned count.

State/persistence: no global state. Ownership of allocated strings transfers to the caller.

Dependencies/integration: implemented by `core-mounts.c` and used by filesystem stressors needing mount candidates.

Risks: caller must not pass an undersized array and must free exactly the count returned.

Test signals: compile consumers and run ownership/leak checks around get/free pairs.
