# File Research: sources/os/plan9/plan9/sys/src/cmd/con/con.c

Interactive connection utility for serial devices and network login sessions. It can dial a byte stream, perform BSD rlogin setup, or open a local device path.

`main` selects simple, rlogin, or device mode from arguments and flags controlling raw/cooked keyboard mode, baud, newline/carriage-return translation, parity stripping, command execution, limited login behavior, and `/srv` posting. `stdcon` forks one process for keyboard-to-network and one for network-to-screen. `fromkbd` handles the `^\` control menu for break, quit, interrupt, return filtering, and shell escapes; `fromnet` filters returns or converts CR to NL.

It depends on Plan 9 networking (`dial`, `netmkaddr`), `/dev/consctl`, notes, rfork, and optional `/srv` registration. It is a user-level terminal bridge rather than filesystem code, but it uses Plan 9 namespace/service conventions.
