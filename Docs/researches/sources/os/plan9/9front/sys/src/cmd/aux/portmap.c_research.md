# File Research: sources/os/plan9/9front/sys/src/cmd/aux/portmap.c

`portmap` is a command-line SunRPC portmapper client. It supports `null`, `set prog vers proto port`, `unset prog vers proto port`, `getport prog vers proto`, and `dump`, defaulting to `dump`.

It builds `SunCall` metadata for the portmapper program/version, dials `udp!portmap`, installs RPC formatters, and dispatches commands through generated `PortT*`/`PortR*` structures. `dump` prints program, version, protocol, and port for each returned map.

Option `-R` enables chatty RPC tracing. Rejected set/unset replies print `rejected`.
