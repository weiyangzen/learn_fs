# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/setup.py.in

## Purpose

This setup template packages the GPFS epoch helper script for installation.

## Important APIs, Types, and Functions

It calls `distutils.core.setup` with package name `gpfs`, version `${GANESHA_VERSION}`, package directory `${CMAKE_CURRENT_SOURCE_DIR}`, package list `['.']`, and generated scripts list `${SCRIPTS_STRING}`.

## Control Flow

CMake configures the template into `setup.py`; build/install commands execute it directly in legacy mode or use modern wheel tooling around it.

## State and Persistence Behavior

It produces build/install packaging artifacts. It has no application runtime state.

## Dependencies and Integration Points

It depends on CMake substitutions and Python packaging. `gpfs-epoch/CMakeLists.txt` is the direct consumer.

## Risks and Edge Cases

`distutils` is deprecated. `packages = ['.']` is unusual and may not behave as intended with modern packaging tools, though the primary payload is a script. Generated script list correctness depends on CMake.

## Test Signals

Package build tests should run both configured setup.py and wheel build paths, then verify the `gpfs-epoch` script is installed and executable.
