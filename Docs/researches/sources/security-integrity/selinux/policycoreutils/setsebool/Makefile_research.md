<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/Makefile -->
# sources/security-integrity/selinux/policycoreutils/setsebool/Makefile

## Purpose
Builds and installs the `setsebool` utility and bash completion.

## Important APIs, Types, And Functions
Defines libselinux/libsemanage include and library paths, `SETSEBOOL_OBJS`, `BASHCOMPLETIONDIR`, and `BASHCOMPLETIONS`. Targets include `all`, `setsebool`, `install`, `relabel`, and `clean`.

## Control Flow
`all` builds `setsebool`. `install` copies the binary to sbin, installs `setsebool.8` and localized man pages, creates the bash-completion directory, and installs `setsebool-bash-completion.sh` as the `setsebool` completion.

## State And Persistence
Build outputs are object and binary files; install persists the executable, man pages, and completion script.

## Dependencies And Integration Points
Depends on libselinux for active booleans and libsemanage for persistent boolean changes.

## Risks And Edge Cases
Completion install only names `setsebool`, while the script also registers `getsebool`; packaging must decide whether that is intended. Relabel is a no-op.

## Test Signals
Compile/link success, staged install of the binary and completion file, and runtime tests for temporary and permanent boolean changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/Makefile -->
