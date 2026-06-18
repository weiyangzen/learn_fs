# sources/storage-engines/wiredtiger/tools/tcmalloc/build-tcmalloc.sh

Purpose: builds a patched `libtcmalloc.so` for a WiredTiger workspace from a supplied source archive URL and source-directory name, placing the result in `TCMALLOC_LIB`.

Important APIs and control flow: runs with `set -euf -o pipefail` and a `die()` helper. It requires exactly `url srcdir`, verifies the repository top level with `git rev-parse`, checks for `CMakeLists.txt`, refuses to overwrite an existing `TCMALLOC_LIB`, requires `bazel` and `/opt/mongodbtoolchain/v5/bin`, downloads the tarball with retrying `curl`, extracts it, writes a Bazel `BUILD` file defining `cc_shared_library(name="libtcmalloc")`, builds with the MongoDB toolchain prepended to `PATH`, then creates `TCMALLOC_LIB` and copies `bazel-bin/libtcmalloc.so`.

State and persistence behavior: downloads an archive into the current working directory, extracts a source tree, writes `${srcdir}/BUILD`, creates `TCMALLOC_LIB`, and copies the shared library there.

Dependencies and integration points: depends on MongoDB toolchain v5, Bazel, curl, tar, git, and the patched tcmalloc archive referenced by Evergreen scripts. The output integrates with `define-with_tcmalloc.sh` and `LD_PRELOAD` workflows.

Risks: it writes into the extracted source tree and current workspace without cleanup. The expected toolchain path is hard-coded. The `srcdir` argument must match the tarball's top-level directory. The comments explicitly prefer prebuilt tcmalloc on spawn hosts, suggesting this is a fallback.

Test signals: successful build leaves `TCMALLOC_LIB/libtcmalloc.so`. Fail-fast checks cover missing workspace, duplicate output, missing Bazel, and missing toolchain.
