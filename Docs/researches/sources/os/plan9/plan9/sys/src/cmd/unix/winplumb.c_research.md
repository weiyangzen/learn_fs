# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/winplumb.c

- Role: Windows helper that listens for TCP commands and launches Windows programs via `ShellExecute`.
- Control flow: Parses `tcp!ip!port`, initializes Winsock, binds/listens, accepts one-line commands, splits executable and argument tail at first space, then invokes `ShellExecute`.
- Helpers: Network byte-order helpers, legacy classful IP parsing, Windows error formatting, and `WinMain` argument splitting.
- Integration: Paired with `winstart`, which sends commands to `tcp!192.168.233.1!17890`.
- Risks/notes: Executes received network strings without authentication; suitable only on trusted/local networks.
