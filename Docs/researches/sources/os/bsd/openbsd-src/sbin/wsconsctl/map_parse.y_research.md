# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/map_parse.y

Yacc grammar for parsing keyboard map assignments.

Accepted forms:
- `keysym sym1 = sym2`: copies the key entry containing `sym2` to the position containing `sym1`.
- `keycode N = [command] sym ...`: assigns command and group symbols for a numeric keycode.

Key behavior:
- Initializes `newkbmap` with `KS_voidSymbol` entries.
- Uses current `kbmap` to resolve existing keysyms for copy operations.
- Automatically fills missing shifted/group symbols using `ksym_upcase()` or group defaults.
- Rejects keycodes >= `KS_NUMKEYCODES`.
- Exposes `newkbmap` for `util.c` to merge back into `kbmap`.

Filesystem/OS relevance:
- Converts textual keymap edits into `struct wskbd_map_data` suitable for kernel ioctls.
