# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccmd.c

Built-in fossil console commands, including an internal 9P client.

The `9p` command builds selected T-messages (`Tversion`, `Tattach`, `Twalk`, `Topen`, `Tread`, `Twrite`, `Twstat`, etc.), writes them through a private pipe-backed console connection, reads the reply, and prints both formatted messages. This lets an administrator exercise the live 9P server from inside the console.

Other commands source command files (`.`), toggle `Dflag`, echo text, and perform Plan 9 namespace `bind`. `cmdInit` creates the private pipe, allocates a console `Con`, marks it as console, and registers the command set.
