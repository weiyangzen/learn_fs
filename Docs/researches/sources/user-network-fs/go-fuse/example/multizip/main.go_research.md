# sources/user-network-fs/go-fuse/example/multizip/main.go

Purpose: mounts a read-only `zipfs.MultiZipFs` filesystem, intended for serving multiple archives selected through config symlinks.

Important flow: parses `-debug`, requires mountpoint, constructs `zipfs.MultiZipFs`, sets one-second entry/attr timeouts, mounts via `fs.Mount`, and waits.

State/dependencies: archive/config state is managed by `zipfs.MultiZipFs`; this file is just the command driver.

Integration/risks: depends on `zipfs` package behavior and FUSE mount availability. Error handling exits process on mount failure. Test signal is build coverage and manual mount/list behavior; no direct automated tests are in this file.
