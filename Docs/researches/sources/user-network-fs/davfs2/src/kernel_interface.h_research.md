<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.h -->
# Research: sources/user-network-fs/davfs2/src/kernel_interface.h

Purpose: public interface between mount/cache setup and the kernel-specific FUSE loop.

Important APIs: `dav_is_mounted_fn` callback type; `dav_init_kernel_interface()` to open/mount the kernel filesystem and update device/buffer data; `dav_fuse_loop()` to process FUSE requests until unmount/termination.

Control flow and integration: `mount_davfs.c` should call `dav_init_kernel_interface` during mount setup, initialize the cache, and then enter `dav_fuse_loop` with the device fd, mountpoint, buffer size, idle time, mount-status callback, run flag, and debug mask.

State and persistence: header declares no state. Implementations create kernel mount state and cache persistence indirectly.

Dependencies: `dav_args` from `mount_davfs.h`, POSIX size/time/int types, and the FUSE/cache implementation files.

Risks: function comments still mention fallback between fuse/coda, but the current implementation is FUSE-focused; stale comments can mislead maintainers. The callback contract for `is_mounted` is important for clean shutdown.

Test signals: compile/link tests across mount helper, integration tests that mount, serve requests, detect unmount, and exit the loop cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/kernel_interface.h -->
