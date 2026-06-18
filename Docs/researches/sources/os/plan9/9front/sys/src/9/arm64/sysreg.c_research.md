# File Research: sources/os/plan9/9front/sys/src/9/arm64/sysreg.c

Dynamic ARM64 system register read/write thunk generator.

Key behavior:
- Builds small executable instruction stubs for arbitrary encoded system registers.
- Caches generated `MRS`/`MSR` stubs in a static buffer.
- Flushes data/instruction caches after emitting new code.
- Provides `sysrd` and `syswr` callable from `KZERO`.

Dependencies:
- Uses cache maintenance, per-CPU `m->machno`, and locking.

Research notes:
- Avoids needing one assembly function per system register while working around immediate register encodings.
