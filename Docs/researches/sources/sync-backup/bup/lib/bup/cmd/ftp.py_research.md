# sources/sync-backup/bup/lib/bup/cmd/ftp.py

## Purpose
`ftp.py` is an interactive or scripted VFS browser for a bup repository. It supports `ls`, `cd`, `pwd`, `cat`, `get`, `mget`, help, and quit-style commands.

## APIs and Control Flow
`do_ls` delegates listing option parsing to `bup.ls`. `write_to_file` streams file contents with `chunkyreader`. Completion helpers use readline hooks and `vfs.contents`. `present_interface(stdin, out, extra, repo)` maintains a resolved VFS `pwd`, tokenizes shell-like input with `shquote.quotesplit`, resolves paths relative to `pwd`, and executes commands. `main(argv)` checks the repository and opens a `LocalRepo`.

## State, Dependencies, Integration, Risks, Tests
Runtime state is limited to current VFS directory and global completion cache/repo. `get` and `mget` write local files in the process working directory, using remote names or supplied local names. Dependencies include `_helpers.readline`, `vfs`, `ls`, `shquote`, `git`, and byte streams. Risks include encoding assumptions in terminal round-trips, local filename overwrite behavior, symlink dereference semantics in `mget`, and completion exceptions. Test signals include scripted command mode, relative path resolution, error messages for missing/non-directory paths, wildcard matching, and readline optionality.
