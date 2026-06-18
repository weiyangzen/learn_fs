# sources/user-network-fs/bazil-fuse/unmount_linux.go

Purpose: This file implements Linux unmounting through the `fusermount3 -u` helper.

Important APIs, types, and functions: `unmount(dir string) error` runs `exec.Command("fusermount3", "-u", dir).CombinedOutput()`.

Control flow: If the helper exits with an error and produced output, the function trims trailing newlines and appends the helper output to the error string before returning it. Successful helper exit returns nil.

State and persistence behavior: No internal state. It requests removal of a live FUSE mount from the OS mount table.

Dependencies and integration points: Depends on `os/exec`, `bytes`, and `errors`. Used by public `Unmount`.

Risks: Requires `fusermount3` in PATH. The returned error is a newly formatted `errors.New`, so callers cannot inspect the original `exec.ExitError` except by parsing text. Busy mounts or permission issues are helper-dependent.

Test signals: Integration tests repeatedly exercise unmount during cleanup but do not directly assert Linux unmount error formatting.
