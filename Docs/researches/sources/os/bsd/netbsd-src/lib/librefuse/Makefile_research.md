# File Research: sources/os/bsd/netbsd-src/lib/librefuse/Makefile

This Makefile builds `librefuse`, NetBSD's FUSE compatibility library implemented on top of puffs and pthreads. It enables fortified-source behavior, names the library `refuse`, and links against `libpuffs` and `libpthread`.

If `DEBUG` is defined, it adds `-g -DFUSE_OPT_DEBUG`. It includes the current directory in the preprocessor path and builds the main high-level, compatibility, logging, low-level, option, and signal source files. It installs `refuse.3` and public headers `fuse.h`, `fuse_opt.h`, `fuse_log.h`, and `fuse_lowlevel.h` into `/usr/include`.

It also includes `refuse/Makefile.inc`, which contributes additional versioned compatibility headers/sources used by the public `fuse.h` API selection layer.
