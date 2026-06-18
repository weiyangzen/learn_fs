# File Research: sources/local-fs/ocfs2-tools/configure.in

## Role

`configure.in` is the Autoconf input for `ocfs2-tools`. It validates the host and dependency environment, computes project version variables, probes optional cluster/GUI/debug features, and declares generated output files.

## Core Configuration

The script requires Autoconf 2.54, initializes against `libocfs2/bitmap.c`, sets package name `ocfs2-tools`, and defines version `1.8.9` plus optional extra version suffix. It rejects non-Linux hosts and requires GCC.

If `CFLAGS` is unset, it applies `-O2` by default or `-g`/`-ggdb` for `--enable-debug`. It initializes compiler, preprocessor, install, symlink, ranlib, and `ar` discovery, then sets root install directories from `--with-root-prefix`.

## Required Dependencies

Required probes include:

- `com_err` through pkg-config or `-lcom_err` plus `et/com_err.h`.
- `uuid` through `-luuid` plus `uuid/uuid.h`.
- `libaio` through `-laio` plus `libaio.h`.
- `readline` through `-lreadline` plus `readline/readline.h`.
- GLib 2.2.3 or newer.

The script also tests whether GLib and `com_err` can be linked statically, which controls whether static fsck or cluster-control builds are allowed.

## Optional Feature Gates

The configure logic sets build flags for:

- `BUILD_DEBUGOCFS2` if readline is available.
- Dynamic vs static fsck/control tools with `--enable-dynamic-fsck` and `--enable-dynamic-ctl`.
- Pacemaker, CMAN, Corosync/OpenAIS CPG, OpenAIS checkpoint, libdlmcontrol, libdlm, FSDLM, CMAP, and `ocfs2_controld`.
- Python 2.3+, Python headers, PyGTK/gobject, blkid, and optional `ocfs2console`.

## Generated Files

It generates `Config.make`, pkg-config files, many man pages, vendor specs/sysconfig docs, optional `ocfs2console` files, and `defragfs.ocfs2/defragfs.ocfs2.8`.

## Notable Limitations

The build system is tied to Linux, GCC, legacy Python 2-era GUI tooling, and older cluster stack APIs. Several optional cluster components degrade to warnings, so a configure success does not imply every tool will be built.
