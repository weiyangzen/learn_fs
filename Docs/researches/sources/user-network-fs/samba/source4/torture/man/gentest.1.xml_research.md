# sources/user-network-fs/samba/source4/torture/man/gentest.1.xml

## Purpose
This DocBook manpage documents `gentest`, a random generic SMB operation differential tester for comparing two SMB servers.

## Important APIs, types, and functions
The XML defines a `refentry` for section 1 with metadata, synopsis, description, options, version, see-also, and author sections. Options documented include two `-U user%pass` credentials, seed, operation count, print operations, backtrack analysis, ignore-field file, oplocks, preset seed file, preset seed usage, fast reconnect, continuous analysis, and analyzing successful runs.

## Control flow
The document explains that `gentest` generates a random operation set, runs it against `//server1/share1` and `//server2/share2`, and displays differences in responses.

## State and persistence behavior
As documentation, the file has no runtime state. It describes a tool that can mutate files on target shares depending on generated SMB operations and seed choices.

## Dependencies and integration points
It uses DocBook XML 4.2 and integrates with Samba's manpage build. The documented semantics should match the `gentest` binary/options.

## Risks and edge cases
Documentation drift is possible: short options may not match current popt names if the program changed. The page is versioned as Samba 4.0 and may omit newer behavior.

## Test signals
Build-time XML validation and generated manpage output indicate structural correctness; user-facing accuracy depends on option parity with the executable.
