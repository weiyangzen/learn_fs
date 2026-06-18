# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/set.go

Purpose: minimal string set implementation used by the parser.

Important APIs: `NewSet`, `Add`, `Remove`, `Contain`, and `ToSlice`. Internally stores keys in `map[string]struct{}` with a package-level empty sentinel.

State and dependencies: no external dependencies; set ordering from `ToSlice` is map-randomized.

Integration points: `sanitizeCmd` uses sets for invalid booleans and invalid options.

Risks and test signals: `ToSlice` is nondeterministic and should not be used where order matters. No direct tests exist; parser tests indirectly cover `Contain`.
