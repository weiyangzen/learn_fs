# File Research: sources/os/bsd/openbsd-src/sbin/kbd/kbd_wscons.c

`kbd_wscons.c` implements wscons keyboard encoding listing and setting for the `kbd` utility. It maps wscons keyboard types to readable families and uses `KB_ENCTAB`/`KB_VARTAB` to translate encoding and variant names.

`kbd_list()` scans `/dev/wskbd0` through `/dev/wskbd9`, opens each keyboard read/write or read-only, obtains keyboard type with `WSKBDIO_GTYPE`, fetches supported encodings with `WSKBDIO_GETENCODINGS`, groups them by keyboard type, and prints available tables.

`kbd_set()` parses an encoding string with optional dot-separated variants, maps it to a `kbd_t`, and applies it to all detected keyboards with `WSKBDIO_SETENCODING`. Unsupported encodings on individual devices are reported without aborting unless the ioctl fails for another reason.

The file is direct device-control code with bounded local parsing and no persistent state.
