# sources/test-tools/xfstests-bld/run-fstests/Makefile

Purpose: install helper for run-fstests assets. It installs the run-fstests tree under `$(prefix)/lib/kvm-xfstests`, installs wrapper scripts under `$(prefix)/bin`, and ensures a root filesystem image is available.

Important targets: `all` prints a message; `install` creates install dirs, archives/extracts the tree with optional `.gitignore` exclusions, removes `config.custom`, copies or downloads `root_fs.img`, and generates `kvm-xfstests`/`gce-xfstests` wrappers from `.in` templates.

Control flow/state: `TEST` probes whether tar supports `--exclude-ignore-recursive`. Persistent outputs are installed library tree, rootfs image, and executable wrappers.

Dependencies/integration: depends on tar, curl, shell, rootfs prebuilt URL, and wrapper templates.

Risks: downloading during install can be surprising or fail offline. Only kvm/gce wrappers are installed here, not android. The tar feature probe is command-output based and may vary by tar implementation.

Test signals: `make install DESTDIR=...` should install scripts, omit `config.custom`, and produce executable wrappers with substituted paths.
