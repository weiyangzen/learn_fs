<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh -->
# sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh

## Purpose
Provides bash completions for `setsebool` and `getsebool`.

## Important APIs, Types, And Functions
Functions are `__get_all_booleans()`, `_setsebool()`, and `_getsebool()`. It calls `getsebool -a` to enumerate names and uses bash `COMP_WORDS`, `COMP_CWORD`, `COMPREPLY`, `compgen`, and `compopt -o nospace`.

## Control Flow
`_setsebool()` offers values after `=`, booleans or `on/off` for recognized boolean names, numeric `0/1`, and options `-N -P -V`. `_getsebool()` offers `-a` and boolean names. The script registers both completion functions at the bottom.

## State And Persistence
No persistent state is written; completions reflect current `getsebool -a` output each invocation.

## Dependencies And Integration Points
Requires bash programmable completion and the `getsebool` binary. It integrates with installed shell completion directories through the Makefile.

## Risks And Edge Cases
`_getsebool()` declares but never assigns `verb`, so its first branches rely on it remaining empty. Frequent `getsebool` calls may be slow on large policies. Completion behavior depends on current word parsing around `=`.

## Test Signals
Source the file in bash and complete options, boolean names, `bool=on/off`, separate `bool 1`, and `getsebool -a` forms.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setsebool/setsebool-bash-completion.sh -->
