# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/setup.py.in

## Purpose

This CMake-substituted setup template packages the `ganeshactl` Python tools and scripts.

## Important APIs, Types, and Functions

The template calls `distutils.core.setup` with package name `ganeshactl`, version `${GANESHA_VERSION}`, package directory `${CMAKE_CURRENT_SOURCE_DIR}`, packages `Ganesha` and `Ganesha.QtUI`, and generated `scripts = [${SCRIPTS_STRING}]`.

## Control Flow

CMake configures this template into a concrete `setup.py`. During build/install, Python executes the setup script to package modules and install script entry files selected by CMake.

## State and Persistence Behavior

It creates build/install artifacts but has no application runtime state.

## Dependencies and Integration Points

It depends on CMake substitutions and Python packaging tooling. `CMakeLists.txt` in the same script area likely supplies `SCRIPTS_STRING` and handles generated UI modules.

## Risks and Edge Cases

`distutils` is deprecated/removed in newer Python environments, so modern builds may need setuptools or PEP 517 tooling. The template assumes generated script names are valid Python list entries. Missing generated UI modules will still package a broken GUI.

## Test Signals

Build tests should configure the template, build/install the package, and import `Ganesha` plus run installed script help paths. Packaging tests under current supported Python versions catch `distutils` issues.
