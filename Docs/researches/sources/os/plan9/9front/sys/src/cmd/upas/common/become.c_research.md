# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/become.c

This file implements a minimal privilege-drop helper.

Key behavior:
- `become` currently only has special behavior for target user `"none"`.
- For `"none"`, it calls `procsetuser("none")`, then installs a new namespace with `newns("none", nil)`.
- On failure it sets an explanatory `%r` error string and returns `-1`.

Integration and risks:
- Called by process-launching helpers in `process.c`.
- Non-`none` users are accepted as no-ops, which is important for understanding privilege expectations.
