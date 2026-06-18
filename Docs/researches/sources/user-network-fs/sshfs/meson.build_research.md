# sources/user-network-fs/sshfs/meson.build

Purpose: Meson build definition for the sshfs executable, man page, install helper, and tests.

Important APIs/types/functions: project `sshfs` C version 3.7.6; global compile arguments; compiler probe for broken `-Wunused-result`; `config.h` with `PACKAGE_VERSION` and platform `IDMAP_DEFAULT`; source list including Darwin compat when needed; dependencies `fuse3 >= 3.1.0`, `glib-2.0`, `gthread-2.0`; executable with `-DFUSE_USE_VERSION=31`; optional `rst2man` manpage target; install helper; `subdir('test')`.

Control flow: configure-time platform and compiler checks adjust defines/sources/arguments, then build targets are declared.

State and persistence behavior: generates build-directory `config.h`, executable, optional man page, copied test scripts, and install artifacts.

Dependencies and integration points: drives all CI workflows and local builds; integrates with `sshfs.c`, `cache.c`, `compat/darwin_compat.c`, and test Meson file.

Risks: old minimum Meson may limit newer features. `IDMAP_DEFAULT` differs by platform, changing runtime default behavior. Optional manpage silently skipped when rst2man is absent.

Test signals: Meson setup on Linux/Darwin/FreeBSD/Alpine, dependency resolution, warning probe behavior, executable build, manpage build when docutils is installed, and test subdir target generation.
