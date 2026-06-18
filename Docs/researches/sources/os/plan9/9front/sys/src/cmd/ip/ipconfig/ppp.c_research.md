# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ppp.c

PPP binding bridge for `ipconfig`. `pppbinddev` forks and execs `/bin/ip/ppp` or `/ppp` with `-uf -p <dev> -x <netmtpt>` and optional baud rate, waits for PPP setup to complete, and then marks `noconfig` because the PPP process performs the IP configuration itself.
