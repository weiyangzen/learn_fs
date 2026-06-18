# File Research: sources/local-fs/gfs2-utils/Makefile.am

## Purpose
Top-level Automake file for `gfs2-utils`. It defines distributed extras, clean targets, subdirectories, gettext/aclocal setup, and an RPM build target.

## Main Elements
- `EXTRA_DIST`: ships `autogen.sh` and `README.md`.
- `MAINTAINERCLEANFILES`: removes generated Autotools/libtool/configure artifacts and generated cluster config headers.
- `SUBDIRS`: builds `po`, `gfs2`, `doc`, and `tests`.
- `RPMSPEC`, `RPMRELEASE`, `RPMBUILDDIR`, `RPMBUILDOPTS`: produce a spec from `tests/gfs2-utils.spec.in` and build an in-place RPM.
- `maintainer-clean-local`: removes the local `m4` macro directory.

## Dependencies And Integration
Depends on Autotools-generated `config.status`, gettext/po integration, and the recursive `gfs2` subdir. RPM packaging expects `rpmbuild` and the generated spec template.

## Risk Notes
The RPM release is derived from `git describe` and falls back to `"0"`, so source tarballs without git metadata may produce generic release values.
