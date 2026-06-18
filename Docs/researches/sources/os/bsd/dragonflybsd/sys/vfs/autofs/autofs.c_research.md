# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.c

## Summary
Implements the autofs control device, automount daemon request queue, trigger retry/cache logic, and shared autofs node tree helpers.

## Main Responsibilities
- Defines `M_AUTOFS`, autofs request/node objcaches, `/dev/autofs` dev ops, global softc, sysctls/tunables, and interruptible signal set.
- Implements RB comparison/generation for autofs node children.
- Implements daemon-ignore detection based on process group of the process using `/dev/autofs`.
- Builds full autofs paths from node ancestry and mountpoint.
- Creates, shares, waits for, times out, retries, and completes automount daemon requests.
- Implements `AUTOFSREQUEST` and `AUTOFSDONE` ioctls.
- Enforces single opener for the autofs device.

## Important Behavior
Trigger requests are keyed by mount/path/key and shared by concurrent waiters. A timeout task marks requests done with `ETIMEDOUT` and wildcard support enabled. Successful requests cache the node for `vfs.autofs.cache` seconds, but failures are deliberately not negatively cached so users can retry immediately.

## Risks
Only one automount daemon instance can open the device; the code relies on stored process group to avoid recursively triggering autofs from automountd descendants. Request taskqueue cancellation/draining occurs while temporarily dropping and reacquiring the softc lock, making refcount/list discipline important.
