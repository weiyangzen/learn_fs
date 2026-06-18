# File Research: sources/os/plan9/9front/sys/src/cmd/pipefile.c

`pipefile.c` binds a Plan 9 pipe endpoint over an existing file path, letting separate reader and writer commands mediate access to the file. Options select read command, write command, and whether to use one duplicated read/write fd or separate read and write opens.

It creates a pipe namespace with `bind("#|", "/n/temp", MREPL)`, replaces the target file with the pipe data file, then starts two `rc -c` commands: one connected from the pipe to the original write fd, and one connected from the original read fd to the pipe. It uses `rfork` with isolated fd/name environment flags and leaves child processes running.
