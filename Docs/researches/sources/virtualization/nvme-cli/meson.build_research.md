# File Research: sources/virtualization/nvme-cli/meson.build

This is the top-level Meson build definition for nvme-cli and bundled libnvme.

Project setup:
- Project name: `nvme-cli`, C language, Meson `>=0.62.0`.
- Version: `3.0-a.5`.
- Licenses: GPL-2.0-only for nvme-cli and LGPL-2.1-or-later for libnvme.
- Default options include GNU99, debugoptimized build, warning level 1, sysconfdir `etc`, and no fallback wraps.

Feature selection:
- Reads Meson options for `nvme`, `libnvme`, `fabrics`, `mi`, `python`, `tests`, `examples`, docs, and optional libraries.
- Disables fabrics/MI/tests/examples on Windows where needed.
- Python bindings require fabrics, libnvme, python dependency, SWIG, and `Python.h`; `-Dpython=enabled` forces libnvme enabled.

Version/config:
- Converts project version into a 2- or 3-component libnvme shared-object version.
- Uses major-only soname for PyPI builds.
- Generates `nvme-config.h` with feature and platform probes.
- Supports `version-tag` override or runs `scripts/meson-vcs-tag.sh`.

Dependency probing:
- json-c, liburing, libkmod, OpenSSL/LibreSSL compatibility, keyutils, dbus, threads, dl, bcrypt/kernel32 on Windows.
- Compiler/platform checks for endian, builtins, `typeof`, byteswap, `isblank`, `sys/random.h`, sed-opal headers, `tm_gmtoff`, fallthrough attribute, statement expressions, Linux MCTP, netdb, sendfile, mmap, reallocarray, and sigaction.

Build structure:
- Adds global C args: `-fomit-frame-pointer`, `-D_GNU_SOURCE`, and `-include <build>/nvme-config.h`.
- Adds special include path handling when nvme-cli links against a separately installed libnvme under a nonstandard prefix.
- Enters subdirs:
  - `ccan`
  - `libnvme`
  - `plugins` and `util` when building nvme executable
  - `unit`, optional `tests`, and `Documentation` under the executable path
- Builds `nvme` executable from core sources including `logging.c`, `nvme-cmds.c`, `nvme.c`, printing modules, plugin sources, util sources, optional `fabrics.c`, and optional JSON printer.

Install/configuration outputs:
- Configures and installs `discovery.conf`.
- Installs dracut rules, systemd units, udev rules, NetworkManager dispatcher scripts, shell completions, and generated spec file.
- Sets install directories from Meson options.

Testing:
- Adds `valgrind` and `asanubsan` test setups on non-Windows.
- `valgrind` setup uses project suppression file and optionally Python suppression file.

Summary:
- Prints paths, dependencies, selected features, and configuration values.

Integration with files in this group:
- Includes `logging.c` and `nvme-cmds.c` in the `nvme` executable source list.
- Enters `libnvme`, where accessor generator targets and libnvme tests are defined.
