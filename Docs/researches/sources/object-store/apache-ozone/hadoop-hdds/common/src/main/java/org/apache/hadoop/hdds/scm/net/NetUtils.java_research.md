# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NetUtils.java

## Purpose
Utility functions for topology path normalization, depth calculation, duplicate exclusion cleanup, ancestor-list derivation, and path suffix handling.

## Important APIs, Types, And Functions
`normalize`, `locationToDepth`, `removeDuplicate`, `getAncestorList`, and `addSuffix` are the public static APIs.

## Control Flow
`normalize` rejects paths not starting with `/` and strips trailing slash except root. `removeDuplicate` mutates excluded node/scope collections to remove redundant exclusions based on ancestor generation. `getAncestorList` gathers unique ancestors for nodes. `addSuffix` appends `/` if absent.

## State And Persistence
Stateless. It mutates caller-provided exclusion collections in `removeDuplicate`.

## Dependencies And Integration Points
Depends on Apache Commons collection/string utilities and SLF4J. Integrated by topology implementations and placement policies.

## Risks And Test Signals
Mutating inputs can surprise callers, and invalid paths throw. Tests should cover null/empty/root paths, invalid relative paths, depth, duplicate exclusion cases, ancestor missing logs, and suffix behavior.
