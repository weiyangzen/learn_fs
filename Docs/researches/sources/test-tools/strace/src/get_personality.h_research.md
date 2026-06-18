# sources/test-tools/strace/src/get_personality.h

Header declaring personality detection support. It exposes the function contract used by trace setup and syscall decoding to select personality-specific syscall tables. It has no state itself. Dependencies are project personality constants and platform headers included by the implementation. Risks are prototype drift or callers using personality values before initialization. Test signals are clean compilation and runtime traces for supported ABI personalities.
