# sources/user-network-fs/mergerfs/vendored/libfuse/util/mount.mergerfs.cpp

## Purpose
`mount.mergerfs.cpp` is a mount helper wrapper that translates `/sbin/mount.*` style invocations into an execution of the mergerfs filesystem binary.

## Important APIs, Types, and Functions
The standalone `main` parses positional source/mountpoint plus `-t` and `-o` options. Helpers `shell_quote` and `add_option` build a safe shell command string.

## Control Flow
The program derives filesystem type from argv[0] names like `mount.fuse.<type>` or `mount.fuseblk.<type>`, parses source and mountpoint, ignores mount manager options such as `nofail`, `user`, `auto`, and `_netdev`, handles `setuid=USER`, preserves real mount options, ensures `dev` and `suid` are added unless disabled by options, splits `type#source` when type is empty, then execs `/bin/sh -c '<type> <source> <mountpoint> -o <options>'`. With `setuid=`, it wraps the command in `su - USER -c`.

## State and Persistence
No internal state persists. It affects the process by execing a shell command and may set `HOME=/root` if no home exists and not switching users.

## Dependencies and Integration Points
It is intended for system mount integration for mergerfs. It depends on `/bin/sh`, optional `su`, and the mergerfs executable matching the derived type.

## Risks
Shell execution is inherently sensitive, but `shell_quote` handles single quotes. Option parsing uses `strtok` on comma-separated options and does not honor escaped commas. `setuid=` causes a shell command through `su`, which depends on system policy and PATH/command availability.

## Test Signals
Test `mount.mergerfs src dst`, `mount.fuse.mergerfs`, `type#source`, `-t fuse.mergerfs`, ignored options, `nodev`/`nosuid`, `setuid=`, source or mountpoint containing quotes/spaces, missing args, and empty type/source errors.
