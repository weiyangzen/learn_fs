# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/sshsession.c

This file implements the server-side session helper that accepts SSH channels from `/net/ssh` and runs shells or commands.

Key behavior:
- Opens a connection clone/data path, consumes an auth capability, optionally enters a new namespace, announces `session`, then listens for session channels.
- For each channel, opens its `request` and `data` files and handles SSH channel requests.
- Starts an interactive shell through `/bin/ip/telnetd -nt` or an exec command through `/bin/rc -lc`.
- Handles supported requests: `shell`, `exec`, `pty-req`, and `window-change`; rejects x11/env/subsystem.
- Closes request/data and interrupts the top process group when the child exits.

Important details:
- Capabilities are written to `#¤/capuse`.
- `-r`/`-R` can set a restricted directory and optionally confine command paths to basenames unless `$sshsession=allow`.
- It can mount the ssh service from `/srv/<srvpt>` if the expected netdir is not visible.
- `newchannel` prevents more than one shell/exec action per channel.

Filesystem relevance:
- Direct: server-side consumer of `/net/ssh/<conn>/<chan>/{listen,request,data}`, `/srv`, namespace setup, and Plan 9 cap devices.
