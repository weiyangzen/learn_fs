# sources/test-tools/xfstests-bld/release/upload-to-korg

Purpose: signs and uploads release artifacts from `release/out_dir` to kernel.org using `kup`, with an optional testing destination.

Important functions: `usage`, `sign_file`, and `upload_file`. `FILES` lists README, root filesystem images/tarballs, and xfstests tarballs for amd64, i386, and arm64.

Control flow: resolves repo root, changes to `release`, processes `--testing`, lists output dir, validates all required files exist, signs each file, then uploads each file and its detached signature. For `.tar.gz`, it signs the uncompressed tar data by gunzipping to `/tmp`.

State/persistence: creates `.sig` files beside artifacts in `out_dir`; uses temporary uncompressed tar files under `/tmp`; uploads or removes remote files under `DEST`.

Dependencies/integration: requires `gpg2`, `kup`, `gunzip`, release output artifacts, and kernel.org upload credentials.

Risks: temporary `/tmp/$tar_fn` names can collide. `upload_file` uses `$i` in destination path instead of local `$1`, relying on loop-global state. No checksum verification after upload. Signing uncompressed tarballs is intentional but different from signing the distributed `.tar.gz` bytes.

Test signals: `--testing` upload, presence of `.sig` files, and kernel.org staging listings validate behavior.
