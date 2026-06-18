# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/as.c

Runs a command as another user on a CPU server.

Key points:
- Opens `#¤/caphash` early and generates a kernel change-uid capability.
- `mkcap` builds `from@to@random`, hashes it with HMAC-SHA1, writes the hash to `caphash`, and returns the capability string.
- `usecap` writes the capability to `#¤/capuse`.
- `becomeuser` switches namespace with `newns`.
- `runas` execs `/bin/rc -lc <cmd>` with `service=rx`.

Dependencies:
- Uses Plan 9 capability device and auth command helpers.

Notable behavior:
- Usage text says `[-c]`, but actual option parsed is `-d`.
