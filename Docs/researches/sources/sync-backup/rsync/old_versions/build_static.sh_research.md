# sources/sync-backup/rsync/old_versions/build_static.sh

## Purpose
`old_versions/build_static.sh` builds a statically linked rsync binary from a historical git tag for cross-version behavior testing. It applies best-effort compatibility patches so old rsync releases can build with modern toolchains and glibc.

## Important APIs, Types, and Functions
The script defines `VERSION`, `TAG`, `ARCHIVE_DIR`, `REPO`, `WORKTREE`, `OUT`, `CFLAGS_OLD`, and a `cleanup()` trap. It uses git worktrees, `perl`, `sed`, `autoheader`, `autoconf`, `configure`, `make`, `ldd`, `strip`, and version checks.

## Control Flow
The script validates a version argument, chooses a tag, creates a temporary worktree from `RSYNC_REPO` or a default path, and registers cleanup. It patches old `lseek64()` redeclarations when present. For trees lacking generated `configure`, it marks `OLD_TREE`, neutralizes problematic `AC_LIBOBJ` fallbacks, and regenerates configure files. It configures with bundled zlib and popt, disables OpenSSL if the option exists, forces `HAVE_GETTIMEOFDAY_TZ` when configure misdetects it, generates `proto.h` and stubs `lib/addrinfo.h` for old trees, then builds with static linker flags. It verifies the binary is static and that `rsync --version` matches the requested version before copying, stripping, and printing file information.

## State and Persistence
Persistent output is `old_versions/rsync_<version>`. Temporary state is a git worktree under `/tmp`, `conf.log`, `make.log`, generated configure/proto files inside the worktree, and patches applied only to that detached worktree.

## Dependencies and Integration Points
The script supports archival compatibility testing outside the normal build. It depends on a local rsync git repository, build tools, static libc availability, bundled dependencies, and old source layout conventions.

## Risks
The default `REPO` path is developer-specific and must usually be overridden. Static linking may fail on distributions lacking static libraries. Compatibility patches are regex-based and best-effort. Disabling fortify and downgrading warnings are intentional for historical behavior but reduce hardening. Version verification assumes the third field of `rsync --version` is the version.

## Test Signals
Tests should build known old tags such as 3.1.3 and 3.2.7, exercise a pre-3.0 tree needing autoconf/proto generation, confirm static linkage with `ldd`, confirm version mismatch failure, verify cleanup removes worktrees, and run the produced binary in client and daemon compatibility scenarios.
