<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd.c -->
# sources/test-tools/strace/tests/ioctl_kd.c

Purpose: exhaustive strace test for Linux keyboard/display (`KD*`, `KDG*`, `KDS*`, `GIO_*`, `PIO_*`) ioctl decoding. It drives invalid fd `-1` plus crafted pointers and payloads so expected output can be compared against strace's decoder without requiring a real console device.

Important APIs/types/functions: Uses raw `syscall(__NR_ioctl)` through `sys_ioctl`, `linux/kd.h`, `linux/keyboard.h`, `struct kbentry`, `kbsentry`, `kbdiacrs`, `kbkeycode`, `kbd_repeat`, `unimapdesc`, `consolefontdesc`, `console_font_op`, and fallback `kbdiacruc/kbdiacrsuc` definitions. Helper functions cover null/invalid pointer handling, screen maps, key entries, function-key strings, diacritics, keycodes, repeat rates, font buffers, unicode maps, color maps, and Unicode diacritics.

Control flow: optional injection setup locks onto an injected `KDGETLED` return. `main` first probes unknown `K` ioctl numbers, then emits grouped decoder checks for speaker/tone commands, LEDs, keyboard type/mode/meta/LEDs, I/O permissions, display mode, screen/font/unicode maps, key tables, signal acceptance, `PIO_UNIMAPCLR`, `KDFONTOP`, and diacritic Unicode tables. Helpers intentionally place buffers at page tails and vary `DEFAULT_STRLEN`, pointer alignment, write/read direction, and known/unknown xlat values.

State and persistence behavior: all state is process-local allocated test memory; no console state should change because calls use fd `-1`. Under syscall injection the same buffers model successful read/write ioctl output so strace must print dereferenced structs and before/after arrows correctly.

Dependencies/integration points: depends on strace test helpers (`tail_alloc`, fill/print helpers, xlat macros, `scno.h`) and kernel UAPI headers. It integrates with strace's xlat modes, syscall injection tests, string truncation logic, pointer fault decoding, and platform word-size formatting.

Risks and test signals: high risk of brittle expected strings because kernel headers, xlat tables, `DEFAULT_STRLEN`, word size, and injected-success behavior all affect output. Test success is exact emitted output ending in `+++ exited with 0 +++`; failures indicate decoder regressions for console ioctls, enum expansion, buffer truncation, or read/write argument classification.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_kd.c -->
