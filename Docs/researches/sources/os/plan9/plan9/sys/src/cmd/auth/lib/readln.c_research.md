# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readln.c

Provides console input helpers for auth commands. `readln` prints a prompt, optionally enables raw console mode, handles backspace and interrupt character, and enforces a fixed buffer length.

`getpass` loops until a password converts with `passtokey`, optionally confirms and runs `okpasswd`. `getsecret` asks whether to assign an Inferno/POP secret and can reuse the Plan 9 password.
