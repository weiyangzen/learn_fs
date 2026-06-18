# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status.js

Purpose: Loads initial Venti web status settings with numeric choices.

Key behavior:
- `loadsettings` sets logging off, stats on, compression to `whack`, compression choices to none/flate/smack/whack, and log names.
- Logging and stats choices are `"0"`/`"1"`.

Dependencies:
- Intended to be used by the web dashboard JavaScript settings renderer.

Notable details:
- Differs from `status1.js`, which uses textual `"off"`/`"on"` choices.
