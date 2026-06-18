# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers.go

## Purpose

`maintainers.go` parses the Linux kernel `MAINTAINERS` file into raw records and converts `F`, `X`, and `N` entries into syzkaller `PathRule` regexes. It is the ingestion layer for deriving subsystem ownership from kernel metadata.

## Important APIs, Types, and Functions

`maintainersRecord` stores name, include/exclude wildcards, regexps, lists, maintainers, and trees. `parseLinuxMaintainers` scans past the header and drives `maintainersLexer.next`. `recordTitle`, `recordProperty`, and `endOfFile` model lexer outputs. `applyProperty` handles selected MAINTAINERS keys. `parseEmail` normalizes tolerant mail syntax. `ToPathRule`, `removeMatchingPatterns`, and `wildcardToRegexp` translate record patterns.

## Control Flow

Parsing skips lines until `Maintainers List`, then alternates between titles and one-letter properties. Dot-prefixed note blocks enter comment mode, and indented comment continuations are ignored. Properties before any title are errors. `F` and `X` values are stored as wildcards, `N` values are validated as regexes, `M` and `L` are parsed as email addresses, and `T` trees are retained for maintainer selection. `ToPathRule` joins include wildcards and `N` regexps with `|`, builds exclude regexps separately, and treats trailing directory patterns as recursive subtree matches.

## State, Dependencies, Risks, and Test Signals

State is local to parsing except that `removeMatchingPatterns` mutates records in place. Dependencies include `bufio.Scanner`, `net/mail`, regex, filesystem separator handling, and `subsystem.PathRule`. Risks include scanner token limits, tolerance that may hide malformed emails, regexp compilation failures for `N`, path-separator portability, and semantic divergence from `get_maintainer.pl`. Tests cover sample parsing, wildcard escaping, include/exclude behavior, directory recursion, match-everything patterns, and fuzz entry coverage.
