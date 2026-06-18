# File Research: sources/local-fs/xfsdump/debian/rules

## Role

This is the Debian package build rules makefile.

## Build Flow

- `build` depends on `built`.
- `built` depends on `config`, runs `make default`, and stamps `built`.
- `config` depends on `.census`.
- `.census` updates autotools config files, builds `include/config.h` with Debian-specific build options, and stamps `.census`.

## Clean Flow

`clean` removes build stamps, runs `make distclean`, removes the package staging directory and debhelper artifacts, restores autotools config files, and runs `dh_clean`.

## Binary Package Flow

`binary-arch` requires root and a completed build, removes/recreates staging, installs into `debian/xfsdump`, runs distribution packaging, and invokes standard debhelper steps such as docs, changelog, strip, compress, fix permissions, shlibs, shlibdeps, control generation, md5sums, and package build.

`binary-indep` is empty, and `binary` depends on both arch and indep targets.

## Environment

The rules export verbose debhelper output and define build options including `DEBUG=-DNDEBUG`, `DISTRIBUTION=debian`, and root install ownership.
