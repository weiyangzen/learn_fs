# sources/storage-engines/sqlite/ext/wasm/mkdist.sh

## Purpose
`mkdist.sh` builds the distributable SQLite JavaScript/WASM zip bundle from the wasm extension build directory. It drives the local Makefile to generate the demo, tester, worker, ESM, and optional 64-bit artifacts, copies the curated public files into a temporary distribution tree, strips comments from selected JavaScript files, then creates a versioned zip archive.

## Important APIs, Types, And Functions
This is a Bash release helper rather than a library. Important flags are `-64`, `-0`, `-1`, `--noclean`, `--snapshot`, and help. `die()` centralizes fatal exits. `fcp()` copies with preserved metadata and makes the destination writable. `scc()` invokes `tool/stripccomments`. The arrays `tgtFiles`, `fTop`, `fJ1`, `fJ2`, and `fW` define the release manifest and comment-stripping policy.

## Control Flow
The script parses arguments, locates `gmake` or `make`, applies default build name `sqlite-wasm`, and optionally appends a dated snapshot suffix. It optionally runs `make clean`, then builds version tooling, comment stripping, and the target files using `emcc_opt`. It recreates `d.dist`, copies top-level demos and common CSS/test utilities, copies wasm files from `jswasm/`, strips comments from selected generated JS/MJS files, asks `./version-info --download-version` for the release version, renames the temporary tree to `<buildName>-<version>`, zips sorted files, lists the archive, and prints the unzipped directory path.

## State And Persistence Behavior
The script deletes and recreates `d.dist`, the final versioned directory, and the final zip. It also invokes Make targets that may rewrite generated wasm/JS artifacts. `--snapshot` embeds the current date in the archive prefix. No source files are intentionally edited, but build outputs and release directories are replaced.

## Dependencies And Integration Points
Dependencies are Bash, GNU-compatible Make, `cp`, `chmod`, `rm`, `mkdir`, `find`, `sort`, `zip`, `unzip`, SQLite's wasm Makefile, `tool/stripccomments`, and `version-info`. It integrates with the canonical wasm build layout, including generated `jswasm` files, demos, `README-dist.txt`, `index-dist.html`, and optional 64-bit artifacts.

## Risks And Test Signals
Risks include unquoted array expansion for paths with spaces, destructive removal of local output directories, stale or missing Make targets, missing `zip`/`unzip`, and manifest drift when new distribution files are added elsewhere. Good validation is to run a normal and `-64` build, inspect `unzip -lv`, confirm no intended public file is missing, verify stripped JS remains loadable, and confirm the zip name uses the expected SQLite download version.
