# sources/test-tools/kdevops/scripts/kconfig/merge_config.sh

## Purpose
`merge_config.sh` merges a base Kconfig `.config` with one or more fragment files, warns about overrides or redundant entries, optionally prevents `y` to `m` demotion, optionally runs a Kconfig make target to resolve defaults/dependencies, and reports requested values that do not survive into the final `.config`.

## Important APIs, Types, And Functions
This is a POSIX shell script. Functional units are `usage()`, `clean_up()`, option parsing, config-symbol extraction via two `sed` expressions, fragment merge loop, optional strict-mode failure, optional `make KCONFIG_ALLCONFIG=... alldefconfig|allnoconfig`, and final requested-versus-actual verification. Options include `-m`, `-n`, `-r`, `-y`, `-O`, `-s`, and `-Q`.

## Control Flow
The script initializes defaults, parses options, chooses `KCONFIG_CONFIG`, creates missing base files, creates temporary merge files, and copies the base into `TMP_FILE`. For each fragment it extracts symbols, detects prior values in the merged temp file, warns or marks strict violations on redefinition, handles `-y` by deleting the demoting value from the fragment instead of the previous built-in value, then appends the fragment. If `-m` is set it copies the merged file directly; otherwise it runs the selected Kconfig target and compares each requested symbol against the resulting config.

## State And Persistence
Temporary files are created in the current directory and removed by an EXIT trap. Persistent output is `KCONFIG_CONFIG`, defaulting to `.config` or `$OUTPUT/.config`. With `-O`, an `O=` make argument is passed and `readlink -m` is used to compute the config path.

## Dependencies And Integration Points
Depends on `/bin/sh`, `mktemp`, `sed`, `grep`, `readlink`, `cp`, and `make`. It is used by build automation that composes kernel/kdevops config fragments before invoking Kconfig resolution.

## Risks And Edge Cases
Many variable expansions are unquoted in `cat`, `grep`, and `sed` commands, so spaces or glob characters in file names can break behavior. Regex deletion with `sed -i "/$CFG[ =]/d"` relies on config symbol safety. `STRICT_MODE_VIOLATED` is only set dynamically. `-Q` sets `WARNOVERRIDE=true`, relying on shell `true` as a no-op command. Output directory handling assumes GNU `readlink -m`.

## Test Signals
Run merges with duplicate symbols, redundant symbols, `# CONFIG_FOO is not set`, `-m`, `-n`, `-s`, `-r`, `-y`, and `-O`. Include fragments whose requested values are rejected by dependencies and verify warnings. Test paths without special characters unless the script is hardened.
