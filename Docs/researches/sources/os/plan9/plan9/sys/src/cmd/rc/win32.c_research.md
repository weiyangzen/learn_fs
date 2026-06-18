# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/win32.c

Read status: complete, 561 lines.

Despite the filename, this is a Plan 9 system-specific backend variant for `rc` in this tree. It uses Plan 9 APIs such as `/env`, `Dir`, `dirread`, `notify`, `exec`, `create`, `remove`, `seek`, and `exits`.

It initializes variables from `/env`, reads shell functions from `/env/fn#*`, updates changed variables/functions back into `/env`, executes commands by searching path entries, scans directories with `dirread`, and converts Plan 9 notes into `rc` trap counters.

Key functions include `Vinit`, `Xrdfn`, `execfinit`, `Waitfor`, `addenv`, `Updenv`, `Execute`, `Globsize`, `Opendir`, `Readdir`, `notifyf`, `Trapinit`, `Executable`, `Isatty`, and `Exit`.

There are visible debug prints in `ForkExecute`, and the file includes comments noting imperfect directory/glob behavior and terminal detection assumptions.

Filesystem relevance: heavy. It uses Plan 9’s file-backed environment, directory reads, executable stat checks, and namespace-visible `/dev/cons`.
