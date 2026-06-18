# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/www/status1.js

Purpose: Defines default Venti web status settings as globals.

Key behavior:
- Sets logging on, stats on, compression to `whack`, compression choices, and log names.
- Logging and stats choices are `"off"`/`"on"`.

Dependencies:
- Intended for inclusion by the Venti HTTP UI.

Notable details:
- Contains no functions; it directly initializes global variables.
