# sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallClobberImmune.cmake

## Purpose

`InstallClobberImmune.cmake` defines an install-time macro for configuration files that should not overwrite administrator-modified files under the install prefix.

## Important APIs, Types, and Functions

The public API is macro `InstallClobberImmune(_srcfile _dstfile)`. It emits an `install(CODE "...")` script using `CMAKE_COMMAND -E compare_files` and `configure_file(COPYONLY)`.

## Control Flow

At install time, the generated script computes `_destfile`, prepending `$ENV{DESTDIR}` when set. If the destination exists, it skips overwriting, compares source and destination, and installs `${_destfile}.example` only when contents differ. If the destination is missing, it copies the source directly to the destination.

## State and Persistence Behavior

The macro persists files during `make install`, either the real destination or a `.example` sidecar. It intentionally avoids clobbering existing config files.

## Dependencies and Integration Points

It is included by `InstallPackageConfigFile.cmake` and used for packaging/install rules for Ganesha configuration files.

## Risks and Edge Cases

The install script uses interpolated paths, so paths containing unusual characters or semicolons require care. `configure_file` inside `install(CODE)` does not update CMake install manifests as a normal `install(FILES)` would, as the comment notes. Directory existence and permissions are assumed to be handled by surrounding install rules.

## Test Signals

Run install into an empty DESTDIR, then install again after modifying the destination. Verify the original file is preserved and an `.example` appears only when content differs.
