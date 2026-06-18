# sources/test-tools/xfstests-bld/fstests-bld/gen-tarball

Purpose: top-level `gen-tarball` builds an xfstests appliance/runtime tarball from built binaries, xfstests, blktests, optional LTP, and version metadata.

Important APIs, types, and functions: shell options `--fast` and `--arch`; config inputs `config.custom` or `config`; environment knobs `ACCEL_BIN`, `TOOLCHAIN_DIR`, `CROSS_COMPILE`, `SOURCE_DATE_EPOCH`; external tools `git`, `make`, `strip`, `find`, `tar`, `gzip`/`pigz`, `cp`, `ln`, and `sort`.

Control flow: loads config, optionally prepends accelerated binaries/toolchain to `PATH`, selects `strip`, parses options, chooses `pigz` if available, sets `SOURCE_DATE_EPOCH` from last git commit if unset, optionally installs LTP into `ltp`, creates `xfstests` either by copying dev tree in fast mode or running `make install`, writes version metadata, copies built binaries/libs/manual pages, handles optional `ima-evm-utils`, creates symlinks for selected LTP/source tools, strips executables, optionally writes build architecture, and creates a reproducible-ish tarball with sorted file list, numeric root ownership, fixed mtime, and write-bit normalization. With `--arch`, it hard-links/copies the tarball to `xfstests-$ARCH.tar.gz`.

State and persistence: deletes and recreates `xfstests`, optionally deletes/recreates `ltp`, writes `xfstests-bld.ver`, `xfstests/git-versions`, `xfstests.tar.gz`, and optional arch-named tarball.

Dependencies and integration points: assumes surrounding fstests-bld directory layout with `xfstests-dev`, `bld`, optional `ltp-dev`, `blktests`, and possibly `../test-appliance/debs`. It consumes outputs from build-all style processes.

Risks: destructive `rm -rf xfstests` and `rm -rf ltp` are expected but dangerous outside the intended directory. `find ... | xargs $STRIP` can fail on no files or unusual names, though errors are ignored in places. Fast mode copies a development tree and may include files that install mode excludes except `.git`/autom4te.cache cleanup. Optional directories are assumed in several copy/link commands.

Test signals: run with `--fast` and full mode in a disposable built tree; inspect tarball contents, ownership, mtimes, `git-versions`, symlinks, optional arch output, and reproducibility across repeated runs.
