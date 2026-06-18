# sources/sync-backup/casync/shell-completion/bash/meson.build

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/shell-completion/bash/meson.build -->
## sources/sync-backup/casync/shell-completion/bash/meson.build

Purpose: this Meson fragment installs the casync bash completion script into a discovered or configured completion directory.

Important declarations: it reads `bashcompletiondir = get_option('bashcompletiondir')`. If empty, it tries `dependency('bash-completion', required : false)` and reads the `completionsdir` pkg-config variable. If that dependency is unavailable, it falls back to `datadir/bash-completion/completions`. If the result is not `"no"`, it installs the `casync` completion file.

Control flow: execution is straightforward at configure time. The install step is conditional only on the final directory value.

State and persistence: no build-time generated state. Install-time state is one completion file under the selected completion directory.

Dependencies and integration points: depends on Meson, the top-level `datadir` variable, `meson_options.txt`, and optionally the `bash-completion` pkg-config package. It is included unconditionally by the top-level build.

Risks: `bashcompletiondir=no` is a string sentinel, not a boolean. Packaging scripts need to pass exactly `-Dbashcompletiondir=no` to disable. If `bash-completion` is missing, the fallback may not match distribution policy. The script assumes the completion source file is named `casync` in this directory.

Test signals: configure with default, explicit path, and `"no"` values. Install dry runs should show the completion installed only when enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/shell-completion/bash/meson.build -->
