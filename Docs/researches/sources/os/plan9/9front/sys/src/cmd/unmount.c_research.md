# File Research: sources/os/plan9/9front/sys/src/cmd/unmount.c

This is a small command wrapper around Plan 9 `unmount()`. It accepts either `unmount mountpoint` or `unmount mounted mountpoint`.

The argument order matches `mount`: optional mounted spec first, mount point second. On failure it reports the mount point and `%r`; on success it exits cleanly.
