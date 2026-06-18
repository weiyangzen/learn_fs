# File Research: sources/virtualization/guestfs-tools/config.sh.in

## Scope

Configure-generated shell fragment exposing selected tool checks to shell scripts.

## Contents

- Preserves configure substitution marker.
- Exports `XMLLINT`.
- Exports `PYCODESTYLE`.

## Risks And Invariants

- Values are substituted by configure.
- Intended for test/support scripts that need configured tool paths.
