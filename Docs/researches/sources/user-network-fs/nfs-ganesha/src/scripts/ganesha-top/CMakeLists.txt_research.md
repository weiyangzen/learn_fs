# sources/user-network-fs/nfs-ganesha/src/scripts/ganesha-top/CMakeLists.txt

## Purpose
This CMake file builds and installs the `ganesha-top` Python administration tool when admin tools and Python 3 are available. It copies `ganesha-top.py` to an extensionless command, generates `setup.py`, builds through legacy distutils or modern wheel tooling, and installs the result.

## Important APIs, Types, And Functions
Key CMake APIs are `add_custom_command`, `configure_file`, `add_custom_target`, and `install(CODE ...)`. Inputs are `setup.py.in` and `ganesha-top.py`; outputs include `ganesha-top`, generated `setup.py`, a timestamp, and optionally a wheel named like `ganesha_top-<major><minor>-py3-none-any.whl`.

## Control Flow
The file is gated by `USE_ADMIN_TOOLS` and `Python3_FOUND`. It strips `.py` from script names, configures `SCRIPTS_STRING`, generates `setup.py`, runs either `setup.py build` or `python -m build --wheel --no-isolation .`, creates the default target `python_ganesha_top`, and installs via either `setup.py install` or `python -m installer`.

## State And Persistence
The build tree holds the copied script, generated setup file, build directories, wheel output, and timestamp. Install writes the command/package into DESTDIR or the CMake install prefix.

## Dependencies And Integration Points
It depends on CMake options and variables `USE_ADMIN_TOOLS`, `USE_LEGACY_PYTHON_INSTALL`, `GANESHA_MAJOR_VERSION`, `GANESHA_MINOR_VERSION`, `GANESHA_VERSION`, `CMAKE_INSTALL_PREFIX`, and Python discovery. Modern mode requires Python `build` and `installer`.

## Risks And Edge Cases
The dependency list references `${GANESHA_TOP_SRCS}` but defines `GANESHA_TOP_SRC`, which can reduce rebuild correctness. `mkdir -p` is less portable than `${CMAKE_COMMAND} -E make_directory`. The expected wheel filename is hand-built and may diverge from Python package normalization. Modern mode assumes required Python packaging modules exist.

## Test Signals
Build `python_ganesha_top` with legacy mode on and off. Inspect generated `setup.py`, confirm the extensionless script exists, verify wheel naming, and run `cmake --install` into a staging prefix.
