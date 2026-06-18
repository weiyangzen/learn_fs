# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/CMakeLists.txt

## Purpose
This CMake file builds and installs the Python DBus administration tool suite under `scripts/ganeshactl`. It handles core `Ganesha` modules, CLI scripts, optional Qt GUI scripts and generated UI Python files, Python package/wheel build and install commands, and the `ganesha_conf.8` man page.

## Important APIs, Types, And Functions
Source lists are `GANESHA_BASE_SRCS`, `SCRIPT_SRC`, `GUI_SCRIPT_SRC`, and `UI_SRC`. CMake APIs include `add_custom_command`, `add_custom_target`, `configure_file`, `install(CODE ...)`, and `install(FILES ...)`. `${PYUIC}` compiles Qt Designer UI files.

## Control Flow
When Python 3 is found, GUI mode optionally compiles `.ui` files and includes GUI scripts. CLI scripts are always copied to extensionless commands. `SCRIPTS_STRING` is generated for `setup.py.in`, then legacy mode runs `setup.py build` and modern mode runs `python -m build --wheel --no-isolation .`. `python_ganeshactl` is built by default. Install uses either `setup.py install` or `python -m installer`. Separately, `ganesha_conf.man` is copied to `ganesha_conf.8`, built by the default `man` target, and installed to man8.

## State And Persistence
Generated state includes copied scripts, generated Qt modules, generated setup file, Python build/wheel artifacts, timestamps, and copied man page. Install state includes Python tools/modules and the man page.

## Dependencies And Integration Points
It depends on Python discovery, `USE_GUI_ADMIN_TOOLS`, `USE_LEGACY_PYTHON_INSTALL`, `${PYUIC}`, Python `build`/`installer` in modern mode, and Ganesha version variables. Runtime integration is through DBus-facing `Ganesha` package modules and command scripts such as `ganesha_stats`.

## Risks And Edge Cases
`GANESHA_BASE_SRCS` are assigned to `GANESHA_SRCS` only in GUI mode, so non-GUI rebuild/package dependencies may miss module changes unless `setup.py.in` compensates. Shell `mkdir -p` is less portable than CMake directory commands. The modern install hard-codes expected wheel naming. The generic `man` target name can collide. The man install destination includes `${CMAKE_INSTALL_PREFIX}` even though CMake destinations are normally prefix-relative.

## Test Signals
Build and install with GUI on/off and legacy on/off. Verify extensionless scripts, optional generated Qt `.py` files, wheel or legacy build outputs, installed modules/scripts, and `ganesha_conf.8` placement. Confirm module source changes trigger rebuilds in non-GUI mode.
