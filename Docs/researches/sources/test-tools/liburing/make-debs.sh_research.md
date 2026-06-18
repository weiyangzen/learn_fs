# sources/test-tools/liburing/make-debs.sh

## sources/test-tools/liburing/make-debs.sh

Purpose: Helper script to create Debian source/build artifacts for a liburing release from the current git tree.

Important commands/flow: accepts optional base dir, computes release dir from `lsb_release`, finds own source dir, derives version from `git describe --match "lib*" | cut -d '-' -f 2`, copies the repo, runs `git clean -dxf`, updates Debian changelog with `dch` if needed, creates tarball and `.orig.tar.gz` symlink, then runs `debuild`.

State and persistence: destructively recreates `$base/<distro>/liburing`, copies source tree, edits copied `debian/changelog`, writes tarballs/symlink, and builds Debian artifacts.

Dependencies/integration: `bash`, git tags, `lsb_release`, `head`, `dch`, `debuild`, Debian packaging metadata.

Risks: `set -xe` exposes commands and aborts on failure. Version parsing assumes tag format matching `lib*` with hyphen-separated output. `readlink -e \`basename $0\`` depends on current working directory containing the script basename. `rm -rf $releasedir` is broad if variables are wrong, though base defaults to `/tmp/release`.

Test signals: successful debuild and generated tar/orig files; changelog version updated to `$version-1`.
