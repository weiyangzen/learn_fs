# sources/test-tools/syzkaller/prog/meta.go

Purpose: stores build-time git revision metadata for diagnostics and panic context.

Important APIs/types/functions: `defaultGitRevision`, globals `GitRevision`, `GitRevisionBase`, `gitRevisionDate`, `GitRevisionDate`, `GitRevisionKnown`, and `init`.

Control flow and state: at init time, strips `+` from `GitRevision` to form `GitRevisionBase`, and parses non-empty `gitRevisionDate` with layout `20060102-150405`, panicking on parse failure. `GitRevisionKnown` reports whether the Makefile injected a non-default revision.

Dependencies and integration: `encoding.go` includes `GitRevision` in deserialization panic context. Build/link steps are expected to fill the globals.

Risks: malformed injected date panics at package init. Unknown revision is normal in ad hoc builds but reduces diagnostic precision.

Test signals: no direct tests in this subset; behavior is simple and indirectly visible in deserialization panic wrapping.
