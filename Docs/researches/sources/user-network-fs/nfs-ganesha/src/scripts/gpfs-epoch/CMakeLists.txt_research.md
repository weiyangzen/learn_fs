# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/CMakeLists.txt

## Purpose

This CMake file builds and installs the GPFS epoch helper script when GPFS FSAL support and Python 3 are enabled.

## Important APIs, Types, and Functions

Within `if(USE_FSAL_GPFS)` and `if(Python3_FOUND)`, it defines `SETUP_PY_IN`, generated `SETUP_PY`, `OUTPUT`, `GPFS_EPOCH_SRCS`, script copy commands, `SCRIPTS_STRING`, `configure_file`, `python_gpfs_epoch` target, and install `execute_process` commands for legacy setup.py or wheel/installer paths.

## Control Flow

CMake strips `.py` from `gpfs-epoch.py` to make an executable script in the build directory, configures `setup.py`, builds either with legacy `setup.py build` or `python -m build --wheel`, and installs via setup.py or `installer`.

## State and Persistence Behavior

It creates build-tree scripts, package metadata, wheel/build artifacts, a stamp file, and install-tree scripts.

## Dependencies and Integration Points

It depends on CMake variables `USE_FSAL_GPFS`, `Python3_EXECUTABLE`, `USE_LEGACY_PYTHON_INSTALL`, `GANESHA_MAJOR_VERSION`, `GANESHA_MINOR_VERSION`, `GANESHA_VERSION`, `CMAKE_INSTALL_PREFIX`, and `LIBEXECDIR`. It packages `gpfs-epoch.py`.

## Risks and Edge Cases

Wheel naming is hard-coded as `gpfs-${GANESHA_MAJOR_VERSION}${GANESHA_MINOR_VERSION}-py3-none-any.whl`, which must match actual build output. The legacy and modern install branches differ in destination handling. Distutils setup template may be dated for current Python packaging.

## Test Signals

CMake configure/build/install tests should cover GPFS enabled/disabled, legacy/non-legacy Python install, wheel file naming, and installed script path.
