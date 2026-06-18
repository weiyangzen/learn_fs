# sources/test-tools/xfstests-bld/build-appliance

Purpose: orchestrates building or updating an xfstests test appliance image/tarball, optionally including a GCE image.

Important APIs and functions: shell script with `usage()`, option parsing via `getopt`, config loading from `config.custom` or `config`, architecture helpers from `run-fstests/util/arch-funcs`, and calls to `fstests-bld`, `run-fstests`, and `test-appliance` tools.

Control flow: parses flags such as `--add-package`, `--chroot`, `--out-tar`, `--out-both`, `--update`, `--gce`, and `--datecode`; sets architecture; runs `update-all` or clean build; generates tarball; optionally starts GCE image creation; runs `test-appliance/gen-image`; then streams and waits for GCE output.

State and persistence: produces `root_fs.img` and/or `root_fs.tar.gz`, may update repository build outputs, may create cloud image artifacts, and writes a temporary `/tmp/gce-xfstests-create.$$` log.

Dependencies and integration: depends on config variables, schroot/sudo, git timestamps, `fstests-bld/build-all`, `gen-tarball`, `gce-xfstests`, and `gen-image`.

Risks: uses `set -e -u`, so unset config variables can abort. Background job control with `wait %./gce-xfstests` is fragile outside interactive-style shells. Package list concatenation converts only the first space to a comma.

Test signals: successful appliance build, generated tarball/image, and optional GCE image creation without unexpected shell exits.
