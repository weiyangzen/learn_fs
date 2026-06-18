# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/vis.h

Read completely: 43 lines.

This compatibility header declares old `unvis` entry points: `unvis`, `__unvis13`, and `__unvis50`. It exists so legacy code can bind to historical unvis symbol versions.

Security/reliability notes: declaration-only; runtime behavior is in the corresponding libc implementations.
