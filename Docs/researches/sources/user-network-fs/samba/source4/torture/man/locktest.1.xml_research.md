# sources/user-network-fs/samba/source4/torture/man/locktest.1.xml

## Purpose
This DocBook manpage documents `locktest`, the randomized locking differential tester implemented by `locktest.c`.

## Important APIs, types, and functions
The XML defines section 1 metadata, synopsis, description, options, version, see-also, and author sections. It documents server/share arguments, optional repeated credentials, seed, operation count, print operations, analysis, oplocks, hide unlock failures, exact error codes, zero/zero locks, lock range/base/min length, and Kerberos.

## Control flow
The page states that the tool runs the same random set of locking operations against two SMB servers and displays response differences.

## State and persistence behavior
The document itself has no state. It describes a tool that creates a test file and manipulates byte-range locks on target shares.

## Dependencies and integration points
It integrates with the Samba DocBook manpage build and should track `locktest.c` command-line options.

## Risks and edge cases
There is visible option-name drift: the source uses long options such as `--num-ops`, `--hidefails`, `--showall`, `--analyse`, and credential-specific `--user1/--user2`, while the manpage documents several short options. Keeping this page aligned with current popt definitions is important for users.

## Test signals
XML build success verifies document structure. Manual comparison with `locktest --help` is the best signal for option accuracy.
