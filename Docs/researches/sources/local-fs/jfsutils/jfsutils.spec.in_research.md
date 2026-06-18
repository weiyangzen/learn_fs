# File Research: sources/local-fs/jfsutils/jfsutils.spec.in

RPM spec template for jfsutils packaging.

Key contents:
- Uses `@PACKAGE@` and `@VERSION@` configure substitutions.
- Metadata: group `System/Kernel`, summary “IBM JFS utility programs”, GPL copyright, JFS/Linux team packager, SourceForge URL.
- Description lists included utilities: `jfs_fsck`, `jfs_fscklog`, `jfs_logdump`, `jfs_mkfs`, `jfs_tune`, and `jfs_debugfs`.
- Build runs `./configure --mandir=/usr/share/man/en/` with RPM CFLAGS, then `make`.
- Install runs `make install DESTDIR=${RPM_BUILD_ROOT}`.
- Files include `/sbin/*`, localized man8 pages, and docs.

Research notes:
- Legacy RPM template; uses old spec tags such as `Copyright` and `Buildroot`.
