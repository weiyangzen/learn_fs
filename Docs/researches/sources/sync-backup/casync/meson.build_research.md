# sources/sync-backup/casync/meson.build

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/meson.build -->
## sources/sync-backup/casync/meson.build

Purpose: the top-level Meson project file configures casync's C build, feature detection, dependencies, generated config header, executables, tests, fuzzers, documentation, completions, and install-time protocol symlinks.

Important APIs and declarations: `project('casync', 'c', version : '2', ...)` sets GNU11 defaults and install dirs. A large `c_args` list enforces warning and hardening flags when supported. `configuration_data()` writes `config.h` values for version, `_GNU_SOURCE`, type sizes, functions (`renameat2`, `copy_file_range`, `getrandom`), compression libraries, and feature toggles. Dependencies include `liblzma`, `zlib`, `libzstd`, `libcurl`, `openssl`, `acl`, optional `fuse`, `selinux`, `udev`, `threads`, and `m`. It builds `casync`, `casync-http`, `notify-wait`, shell completions, docs, tests, fuzzers, and tag targets.

Control flow: configuration detects compiler support and selected options, then enters `src`, `test`, `shell-completion/bash`, and `doc`. It creates executables from source lists populated by subdirs. It configures shell test scripts with paths and feature booleans, registers unit tests, and conditionally installs udev rules. It creates protocol symlinks for `casync-https`, `casync-ftp`, and `casync-sftp`.

State and persistence: build state includes `config.h`, configured test scripts, generated udev rules, executable outputs, installed binaries, protocol symlinks, and optional man/completion artifacts. Source state is not mutated except build-directory postconf symlinks.

Dependencies and integration points: central integration point for all C modules in `src`, tests in `test`, fuzzers, Sphinx docs, bash completion, and udev. It also injects `-include config.h` into all C compilation.

Risks: `auto_features=enabled` plus required dependencies can make configuration strict by default. The udev rule dir auto-detection assumes `udev.pc` provides `udevdir`; if not found with `udev=true`, this can fail. Install/postconf symlink scripts assume Unix shell behavior. Test timeouts are long and may need privileged features for FUSE/NBD.

Test signals: `meson test` covers shell scripts, C unit tests, help output tests, and fuzzer binary builds. Configuration with different feature options is important because `CA_COMPRESSION_DEFAULT` and optional code paths depend on generated macros.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/meson.build -->
