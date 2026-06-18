# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ppp.c

Adapter that lets `ipconfig` delegate interface binding/configuration to `/bin/ip/ppp`.

Key behavior:
- `pppbinddev` clears `/net/ndb` if no IP interfaces exist.
- Forks and execs `ppp -uf -p <dev> -x <mpoint>` plus optional baud.
- Waits for PPP to complete connection/configuration.
- Sets `noconfig = 1` because PPP created the IP interface itself, then reads resulting NDB state via `getndb`.

Integration points:
- Called by `binddevice` in `ipconfig/main.c` when `conf.type == "ppp"`.
- Uses shared globals `conf`, `nip`, `noconfig`.

Risks and notes:
- Falls back from `/bin/ip/ppp` to `/ppp`.
- Treats any non-empty PPP child status as fatal.
