# sources/test-tools/cthon04/tools/Makefile

## Purpose
This Makefile builds the Connectathon auxiliary network and directory tools: TCP/UDP ping clients and daemons, directory printers/dumpers, and portmapper tests.

## Important APIs, Types, and Functions
Key variables and targets are `TESTS`, `include ../tests.init`, `all`, individual compile rules for `tcp`, `tcpd`, `udp`, `udpd`, `dirdmp`, `dirprt`, `pmaptst`, `pmapbrd`, plus `lint`, `clean`, `copy`, and `dist`.

## Control Flow and State
`all` compiles every listed tool with inherited compiler flags and libraries. Comments document an alternate Linux `TESTS` set that omits unsupported `dirdmp`. `copy` installs built binaries to `DESTDIR`, while `dist` copies Makefile, README, and all C sources.

## Persistence and Dependencies
Persistent state is object files, tool binaries, and copied distribution files; `clean` removes objects and binaries. Dependencies: `../tests.init`, C compiler, RPC/socket libraries as needed, and a writable `DESTDIR` for copy/dist.

## Integration Points, Risks, and Test Signals
Integration is with manual/tooling support for Cthon network and directory diagnostics. Risks include the Linux dirdmp caveat requiring manual Makefile edits, no automatic header dependencies, and destructive overwrite in `copy`. Test signals are all listed binaries building and the client/server tools successfully exchanging messages.
