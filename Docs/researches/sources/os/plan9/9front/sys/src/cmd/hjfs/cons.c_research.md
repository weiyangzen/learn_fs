# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/cons.c

Implements the administrative console command service for `hjfs`.

Key points:
- Creates `/srv/<service>.cmd` backed by a pipe and a console process.
- Parses line-oriented commands with up to 16 arguments.
- Commands include:
  - `sync`
  - `halt`
  - `dump`
  - `allow`
  - `disallow`
  - `noauth`
  - `chatty`
  - `create`
  - `newuser`
  - `users`
  - `echo`
  - `df`
  - debug commands for dentries and block lookup/modification
- `walkpath()` resolves absolute paths through `Chan` operations.
- `cmdcheck()` scans reference blocks and validates referenced data/dentry/indir/ref/superblock blocks, though it is commented out of the command table.
- `cmdcreate()` creates a file or directory with specified owner, group, permissions, and flags.
- `cmddf()` reports free/used/total block counts and MB equivalents.
- Debug commands inspect dentry location, raw dentry bytes, and block mappings for a file.
- `consproc()` tokenizes commands, validates arity, invokes handlers, and prints errors through `dprint`.

Dependencies and interactions:
- Uses channel operations and buffer functions from the core filesystem.
- Calls `fsdump()`, `sync()`, `shutdown()`, `readusers()`, `cmdnewuser()`, and `dprint()`.

Research relevance:
- Operational control surface for `hjfs`, including maintenance, permission toggles, user management, and low-level diagnostics.
