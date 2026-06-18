# File Research: sources/os/bsd/freebsd-src/sbin/devd/devd.cc

## Purpose
Implements the device event daemon: parses configuration, listens to `/dev/devctl`, exposes client sockets, expands event variables, matches rules, and runs actions.

## Main Elements
- Classes: `var_list`, `match`, `media`, `action`, `event_proc`, and `config`.
- `my_system()`: fork/execs `/bin/sh -c`, closes descriptors except stdio, and preserves signal state.
- Matching: regular-expression match with optional leading `!` inversion, media-type checks through `SIOCGIFMEDIA`, and priority-sorted attach/detach/nomatch/notify rule lists.
- Config parsing: reads main config, then `.conf` files from configured directories, sorts rule lists by descending priority, and manages pidfile lifecycle.
- Expansion: supports `$var`, `$*`, `$_`, `$$`, and leaves `$(...)` shell command substitutions intact; shell action variables are shell-quoted.
- Event processing: parses `!`, `?`, `+`, and `-` devctl records into variables, adds timestamp and `vm_guest`, then runs the first matching rule list entry.
- Client sockets: creates world-writable stream and seqpacket Unix sockets under `/var/run`, tracks up to configurable clients, sends events, and drops unresponsive clients.
- `main()`: checks/enables `hw.bus.devctl_queue`, parses `-d`, `-f`, `-l`, `-n`, `-q`, loads config, daemonizes when requested, installs signal handlers, and enters the event loop.

## Dependencies And Integration
Uses lexer/parser generated from `token.l` and `parse.y`, `libutil` pidfile helpers, `/dev/devctl`, sysctls, Unix-domain sockets, and shell/userland actions.

## Risk Notes
Actions run as shell commands with expanded event variables. The implementation shell-quotes variable substitutions but intentionally preserves `$(...)` command substitution in config strings. Event storms are bounded by socket send buffers and client limits.
