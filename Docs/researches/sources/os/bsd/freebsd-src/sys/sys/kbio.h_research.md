# File Research: sources/os/bsd/freebsd-src/sys/sys/kbio.h

Keyboard ioctl and keymap ABI header. It defines keyboard modes (`K_RAW`, `K_XLATE`, `K_CODE`), lock and LED bits, keyboard type values, tone/sound/io-access ioctls, keyboard info, repeat-rate tables, and mux add/release controls.

Keymap support includes constants for key counts, states, dead keys, accent chars, function keys, and structures `keyent_t`, `keymap`, `accentmap`, `keyarg`, `fkeytab`, and `fkeyarg`. FreeBSD 13 compatibility structs preserve older byte-sized keymap layouts.

It defines special key codes for shift/control/alt, screen switching, function keys, accent/dead keys, debug/reboot/halt/paste actions, and output flags such as no-key, function-key, meta, backtab, special, release, and error. `KEYCHAR` and `KEYFLAGS` split packed key returns.
