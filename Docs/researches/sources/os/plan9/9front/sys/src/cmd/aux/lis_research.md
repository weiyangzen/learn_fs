# File Research: sources/os/plan9/9front/sys/src/cmd/aux/lis

Role: Tiny rc wrapper around `aux/listen`.

Behavior:
- Executes `aux/listen -t /sys/src/cmd/aux tcp`.

Purpose:
- Starts trusted TCP service listening using service programs from `/sys/src/cmd/aux`.
