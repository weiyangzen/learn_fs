# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/setup.py.in

## Purpose
This is the CMake-configured Python packaging template for `ganesha-top`. It produces a `setup.py` used by legacy distutils builds or by modern wheel build commands driven from CMake.

## Important APIs, Types, And Functions
The file imports `setup` and unused `Extension` from `distutils.core`. Under `if __name__ == '__main__'`, it calls `setup` with name, version, author/maintainer metadata, source package directory, and `scripts = [${SCRIPTS_STRING}]`.

## Control Flow
Execution is a single `setup(...)` call after CMake substitutes `${GANESHA_VERSION}`, `${CMAKE_CURRENT_SOURCE_DIR}`, and `${SCRIPTS_STRING}`.

## State And Persistence
The template has no direct state. Generated `setup.py` contributes build/install artifacts in the CMake binary and install trees.

## Dependencies And Integration Points
It depends on CMake substitution and Python distutils/setuptools-compatible behavior. It is coupled to `ganesha-top/CMakeLists.txt`, which constructs `SCRIPTS_STRING` and selects legacy or wheel build/install mode.

## Risks And Edge Cases
`distutils` is deprecated or unavailable in newer Python distributions. `package_dir` is set without a `packages` list, so only scripts are effectively packaged unless other tooling adds packages. CMake's expected wheel filename must match Python packaging normalization and version substitution.

## Test Signals
Inspect generated `setup.py` for unsubstituted placeholders, run `python3 setup.py --name`, and build through both CMake packaging branches. Confirm generated wheel/package naming matches the CMake install command.
