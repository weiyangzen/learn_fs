# sources/test-tools/strace/src/kd_ioctl.c

Purpose: decodes non-mpers Linux keyboard, console, and VT ioctl commands.

Important APIs/types/functions: `kd_ioctl`, helpers `kiocsound`, `kd_mk_tone`, `kd_leds`, `kd_get_kb_type`, `kd_io`, `kd_set_mode`, `kd_get_mode`, `kd_screen_map`, `kd_uni_screen_map`, `kd_kbd_entry`, `kd_kbd_str_entry`, `kd_diacr`, `kd_diacr_uc`, `kd_keycode`, `kd_kbdrep`, `kd_font`, `kd_kbmeta`, `kd_unimapclr`, `kd_cmap`, and many `kd_*` xlat tables.

Control flow: `kd_ioctl` truncates the argument to current tracee word size and dispatches by ioctl code. Simple setters print immediate values; getters generally return 0 on entry and decode pointed-to data on exit. Complex commands decode keyboard maps, strings, diacritic arrays, keycodes, repeat settings, font/cmap buffers, and signal values, using entry/exit comparisons where the kernel may update structures.

State and persistence behavior: per-call private state stores original keycode for `KDGETKEYCODE` so exit can report changed values. Other handlers are stateless apart from normal entry/exit phase behavior and tracee memory reads.

Dependencies and integration points: integrates with the tty ioctl dispatcher and falls through to `kd_mpers_ioctl` for personality-dependent font/unimap structures. It depends on Linux KD/keyboard headers, generated xlat tables, `print_fields.h`, and tracee memory/string printers.

Risks: ioctl direction semantics are easy to invert; many commands only decode useful data on exit. Array lengths are kernel constants and must remain bounded. Keyboard value comments depend on xlat verbosity and key type classification.

Test signals: cover sound/tone comments, LED get/set/default LEDs, mode get/set, screen maps, Unicode screen maps, keyboard entries and strings, diacritic truncation above 256 entries, keycode value-change printing, font/cmap error paths, and fallback to mpers handlers.
