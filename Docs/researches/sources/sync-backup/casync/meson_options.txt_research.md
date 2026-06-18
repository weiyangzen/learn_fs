# sources/sync-backup/casync/meson_options.txt

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/meson_options.txt -->
## sources/sync-backup/casync/meson_options.txt

Purpose: this file defines Meson project options controlling optional integrations, compression support, fuzzing modes, man page generation, udev install paths, and bash completion installation.

Important options: boolean `fuse`, `selinux`, and `udev` default to true. `udevrulesdir` allows overriding the rules install directory. `man` controls Sphinx man page generation. Feature options `libzstd`, `liblzma`, and `libz` control compression library linking. Booleans `oss-fuzz` and `llvm-fuzz` select fuzzer integration modes. `bashcompletiondir` controls shell completion install path, with `"no"` disabling installation.

Control flow: options are read by the top-level and subdirectory Meson files. The top-level build rejects enabling both fuzzing modes, resolves dependencies based on these settings, writes feature macros into `config.h`, and controls installation of udev rules, docs, and completions.

State and persistence: no direct runtime state. These options influence generated build outputs, installed files, and compiled feature availability.

Dependencies and integration points: maps directly into dependency detection in `meson.build`, `doc/meson.build`, and `shell-completion/bash/meson.build`. Compression options affect `cacompression.h` through generated `HAVE_LIB*` macros.

Risks: default true values for FUSE, SELinux, and udev can make builds fail on systems without development packages unless users disable them. The `man` option description is missing a closing parenthesis. The fuzz options are typed boolean but use string-looking default values `'false'`; Meson accepts booleans more idiomatically as `false`.

Test signals: option matrix builds should verify `-Dfuse=false`, `-Dselinux=false`, `-Dudev=false`, compression library combinations, `-Dman=false`, and each fuzzer mode independently.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/meson_options.txt -->
