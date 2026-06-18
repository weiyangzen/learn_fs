# File Research: sources/os/plan9/9front/sys/src/cmd/sam/parse.h

`parse.h` defines sam's parsed command/address structures and command-table metadata.

`Addr` represents address parse nodes: type, optional regex or left-side address, numeric argument, and next/right-side pointer. `Cmd` represents commands with an address, regex, command/text/address union argument, command-list chaining, numeric argument, flag, and command code.

`Cmdtab` describes each command's grammar and execution function: command character, text/regex/address/count/token requirements, default nested command, default address behavior, and function pointer.

`Defaddr` defines default-address classes: no address, dot, or whole file. The header also declares all command implementation entry points and parser/evaluator helpers used across `cmd.c`, `address.c`, and `xec.c`.
