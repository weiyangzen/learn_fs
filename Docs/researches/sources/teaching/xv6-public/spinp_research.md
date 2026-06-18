# File Research: sources/teaching/xv6-public/spinp

Shell helper for running SPIN model checker workflows.

Behavior:
- Requires one `.p` file.
- Deletes old trail, runs `spin -a`, compiles generated `pan.c`, runs `pan -i`, removes generated artifacts, and displays a counterexample trace if a trail exists.

Role:
- Verification aid for Promela models, not part of xv6 build/runtime.
