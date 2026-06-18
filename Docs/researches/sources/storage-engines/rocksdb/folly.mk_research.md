<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/folly.mk -->
# sources/storage-engines/rocksdb/folly.mk

## Purpose

`folly.mk` centralizes RocksDB's Makefile integration for Folly. It supports two modes: linking against a full Folly build (`USE_FOLLY=1`) or compiling a lightweight source-picked Folly variant (`USE_FOLLY_LITE=1`). It also defines checkout/build targets and cache helpers so CI can pin and build a known Folly revision.

## Important APIs, Types, and Functions

- `USE_FOLLY` and `USE_FOLLY_LITE` are mutually exclusive build modes.
- `FOLLY_PATH`, `BOOST_PATH`, `DBL_CONV_PATH`, `GFLAGS_PATH`, `GLOG_PATH`, `LIBEVENT_PATH`, `XZ_PATH`, `LIBSODIUM_PATH`, and `FMT_PATH` drive include/library discovery for full Folly builds.
- `PLATFORM_CCFLAGS`, `PLATFORM_CXXFLAGS`, and `PLATFORM_LDFLAGS` are augmented with include paths, defines, libraries, and rpaths.
- `FOLLY_COMMIT_HASH` pins public CI to a specific Folly revision.
- `restore_folly_getdeps_downloads` and `cache_folly_getdeps_downloads` are make macros for download cache reuse and fallback mirrors.
- `checkout_folly` clones/fetches Folly, resets to the pinned commit, applies local source patches, and fetches boost/fmt.
- `build_folly` clears the getdeps install root, restores downloads, runs getdeps build, and patches rpath for glog/gflags.

## Control Flow

When `USE_FOLLY=1`, the Makefile rejects simultaneous `USE_FOLLY_LITE=1`, discovers dependency paths relative to `FOLLY_PATH` if set, adds include flags with AIX-specific `-I` handling, links static Folly/dependencies plus debug or release variants of fmt/glog/gflags, and defines `USE_FOLLY`/`FOLLY_NO_CONFIG`.

When `USE_FOLLY_LITE=1`, it uses `third-party/folly` as source, optionally discovers boost and fmt source includes, adds Folly include flags and defines, and links `-lglog`. The `checkout_folly` target ensures the source tree is present and pinned, modifies two Folly files for RocksDB's CI compatibility, restores/fetches dependency downloads, and refreshes the cache. `build_folly` rebuilds via getdeps with flags matching RocksDB debug mode and compiler `-m*` flags.

## State and Persistence Behavior

This file mutates the working tree and `/tmp/rocksdb-getdeps-cache` when checkout/build targets run. It creates or updates `third-party/folly`, resets it to a pinned commit, patches source files in place, populates getdeps downloads/install directories, and can remove the previous getdeps install root before rebuild. Build variables affect later RocksDB compile/link commands but are not persisted except through generated/build outputs.

## Dependencies and Integration Points

It integrates with RocksDB's top-level Makefile and `make_config.mk`, Git, Python getdeps, pkg/build tooling, patchelf, fallback mirror script `build_tools/getdeps_fallback_mirror.py`, platform detection, and CI cache actions. It assumes Folly's getdeps directory layout and dependency naming conventions.

## Risks and Edge Cases

The full Folly path discovery uses shell `ls -d` patterns and can break if dependency directory names change or multiple matches produce ambiguous whitespace. `checkout_folly` runs `git reset --hard` inside `third-party/folly`, which is intentional but destructive to local Folly edits. Local Perl patches are brittle against upstream file changes. Debug/release library name differences and rpath handling are platform-sensitive. The file itself says the integration simulates Meta-internal Folly and is not validated for general use.

## Test Signals

Signals are successful `make checkout_folly`, `make build_folly`, RocksDB build with `USE_FOLLY=1`, RocksDB build with `USE_FOLLY_LITE=1`, cache hit/miss behavior when `folly.mk` changes, AIX include handling, debug/release link success, and runtime resolution of glog/gflags shared libraries after patchelf.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/folly.mk -->
