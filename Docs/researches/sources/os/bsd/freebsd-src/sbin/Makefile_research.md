# File Research: sources/os/bsd/freebsd-src/sbin/Makefile

## Purpose
Top-level FreeBSD `sbin` build directory makefile. It enumerates base system administrative utilities built under `/sbin`.

## Main Elements
- Includes `src.opts.mk` and `bsd.arch.inc.mk` for build option and architecture conditionals.
- Defines core `SUBDIR` entries such as `adjkerntz`, `camcontrol`, `fsck`, `ifconfig`, `mount`, `newfs`, `route`, `sysctl`, and `umount`.
- Adds optional subdirectories based on `MK_*` knobs: networking, CCD, HAST, IPFilter, IPFW, OpenSSL, PF, quotas, routed, Veriexec, ZFS, and tests.
- Sets `SUBDIR_PARALLEL=` to enable subdir parallelism under FreeBSD bmake semantics.
- Includes `bsd.prog.mk` and `bsd.subdir.mk`.

## Dependencies And Integration
This is build orchestration only. It ties `sbin` utilities into the FreeBSD source tree option framework and controls whether ZFS-dependent `bectl` and `zfsbootcfg` are included.

## Risk Notes
Build membership depends on `MK_*` options. Missing a conditional here silently excludes utilities from system builds.
