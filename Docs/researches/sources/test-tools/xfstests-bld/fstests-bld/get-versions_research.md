# sources/test-tools/xfstests-bld/fstests-bld/get-versions

Purpose: `get-versions` prints a sorted summary of git descriptions and commit dates for fstests-bld and its component repositories.

Important APIs, types, and functions: shell script using `git describe --always --dirty` or `--tags` for some repos, `git log -1 --pretty=%cD`, temporary directory `tmp-$$`, and optional copying of `.ver` files from e2fsprogs and test appliance debs.

Control flow: creates a temp directory, writes `xfstests-bld.ver`, copies `e2fsprogs.ver` if present, enters each known repository and writes a component `.ver` file, conditionally handling optional dirs, copies external deb version files, concatenates sorted `.ver` files, removes the temp directory, and exits 0.

State and persistence: creates and removes `tmp-$$`. It reads git metadata from many sibling repositories and emits summary to stdout.

Dependencies and integration points: assumes required directories like `fio`, `quota`, `ima-evm-utils`, `xfsprogs-dev`, and `xfstests-dev` exist. `gen-tarball` creates similar version metadata for inclusion in tarballs.

Risks: no `set -e`, so failures may be partially ignored. It unconditionally `cd`s into `ima-evm-utils`, which `get-all` treats as optional; absence will cause noisy failures and follow-on path errors. `TMPDIR=tmp-$$` can collide only rarely but is not cleaned on interruption.

Test signals: run in a populated checkout and compare expected component rows. Test missing optional and missing required directories, dirty trees, and cleanup of temporary directory.
