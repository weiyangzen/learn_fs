# sources/user-network-fs/nfs-ganesha/src/cmake/modules/InstallPackageConfigFile.cmake

## Purpose

`InstallPackageConfigFile.cmake` wraps installation of user-editable configuration files. It chooses normal package-manager install semantics in binary packaging mode and clobber-immune install behavior for local installs, while also creating explicit example-config targets.

## Important APIs, Types, and Functions

The public API is macro `InstallPackageConfigFile(_srcfile _dstdir _dstfilename)`. It uses `InstallClobberImmune`, `install(FILES)`, cache variable `INSTALLED_CONFIG_FILES`, target `install-example-configs`, and per-file target `install-example-config-<flattened-src>`.

## Control Flow

The macro builds `_dstfile`. In `BINARY_PACKAGING_MODE`, it installs the source normally, records the installed config path in `INSTALLED_CONFIG_FILES`, and on Apple also installs a `.example` file. Otherwise it delegates to `InstallClobberImmune`. It then ensures a top-level example target exists, flattens slashes in the source path for a legal target name, creates a custom target that copies the source to `${DESTDIR}${_dstfile}.example`, and adds it as a dependency.

## State and Persistence Behavior

It creates install rules, custom targets, and a cache string recording config files for package scripts. Runtime installation may write real config files and example files.

## Dependencies and Integration Points

It depends on `InstallClobberImmune.cmake`, CMake install/custom target support, and package scripts that consume `INSTALLED_CONFIG_FILES`.

## Risks and Edge Cases

Flattening only replaces `/`, so other target-name-problem characters in source paths may remain. The custom example target uses `DESTDIR` expansion in a CMake command context and assumes the destination directory exists. The cache string accumulates space-separated paths, which can be fragile for paths with spaces.

## Test Signals

Configure with and without `BINARY_PACKAGING_MODE`, run normal install and `install-example-configs` into DESTDIR, and verify package scripts see `INSTALLED_CONFIG_FILES`.
