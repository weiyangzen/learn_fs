<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/Makefile -->
# sources/security-integrity/selinux/python/chcat/Makefile

## Purpose
Installs the `chcat` Python MLS category management script and man pages.

## Important APIs, Types, And Functions
Defines `PREFIX`, `BINDIR`, `MANDIR`, `LINGUAS`, and targets `all`, `install`, `clean`, `relabel`, and `test`. `all` depends on the `chcat` script.

## Control Flow
`install` creates the binary directory, installs `chcat` mode 755, creates man8 directory, installs `chcat.8`, and installs localized man8 pages for selected languages.

## State And Persistence
The install persists the executable script and documentation. There are no build products beyond the source script.

## Dependencies And Integration Points
The script itself depends on Python SELinux bindings, `seobject`, `chcon`, and `semanage`; this Makefile only places it in the target image.

## Risks And Edge Cases
No syntax/test target is implemented, so packaging can install a script that has not been exercised. `relabel` is a no-op.

## Test Signals
Run `python3 -m py_compile` or script help manually, staged install checks, and functional MLS category tests on an MLS-enabled SELinux system.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/chcat/Makefile -->
