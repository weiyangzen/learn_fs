# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/wiki.h

Shared data model and function declarations for `wikifs` and its helper tools.

Key contents:
- Defines cache limits: `Tcache`, `Maxmap`, and `Maxfile`.
- Enumerates parsed wiki node types (`Wpara`, `Wheading`, `Wbullet`, `Wlink`, `Wman`, `Wplain`, `Wpre`, `Whr`) and template types.
- Defines `Wpage`, `Whist`, `Wdoc`, substitution records, map elements, and reference-counted maps.
- Declares parser, formatter, cache/storage, map lookup, write, utility, and wiki-directory-relative file APIs.
- Exposes global `map`, `maplock`, and `wikidir`.

Notable dependencies:
- Uses Plan 9 `String`, `Biobuf`, `Ref`, `Qid`, and `RWLock` types from including compilation units.

Research notes:
- Header couples all wiki helper programs to the same storage and rendering API.
