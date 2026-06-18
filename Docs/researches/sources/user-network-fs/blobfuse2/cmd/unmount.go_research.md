# sources/user-network-fs/blobfuse2/cmd/unmount.go
## sources/user-network-fs/blobfuse2/cmd/unmount.go

Purpose: implements `blobfuse2 unmount <mount path>` with exact path, wildcard path, lazy unmount, and shell completion support.

Important APIs/functions: global `unmountCmd`, `unmountBlobfuse2`, and `init` registration of the `--lazy/-z` persistent flag plus `umntAllCmd`.

Control flow: the command requires one argument and reads the `lazy` flag. If the path contains `*`, it treats the argument as a regexp pattern, lists blobfuse mount points with `common.ListMountPoints`, and unmounts matches. Otherwise it unmounts the given path. `unmountBlobfuse2` tries `fusermount3` then `fusermount`, adds `-z` for lazy mode, runs `-u <path>`, logs and prints success, and returns the stderr plus exec error on failure. It only tries the second binary when the previous error says the executable was not found.

State and persistence: changes OS mount state. It does not persist local files. It writes user-visible success to stdout unless `silent` is true and logs success/failure.

Dependencies/integration: Cobra, `common.ListMountPoints`, `fusermount3`/`fusermount`, regexp matching, and the logger.

Risks: wildcard matching passes the user path directly to `regexp.MatchString`; literal paths containing regex metacharacters can match unexpectedly. The shared `errb` buffer is not reset between binary attempts. Error detection depends on the text `executable file not found`. Mount listing is Linux `/etc/mtab` based.

Test signals: `unmount_test.go` mounts loopbackfs instances with the built binary and checks normal, busy, wildcard, completion, lazy, and invalid mount flag behavior.
