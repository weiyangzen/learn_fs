# sources/storage-engines/pebble/sstable/internal/genprops/gen_props.go

## Purpose
Generates `sstable/properties_gen.go` from `Properties` struct tags, replacing reflection with explicit load/encode/string code.

## Important APIs, Types, and Functions
- `Field` describes a tagged property field: Go name, property tag, kind, encode-empty flag, and intern flag.
- `tmpl` is the generated source template containing `Properties.load`, `encodeAll`, `isLoaded`, `String`, and bit constants.
- `zeroVal` returns literal zero values for template comparisons.
- `main` loads the `sstable` package, finds the `Properties` struct, extracts `prop` and `options` tags, validates supported types and bitfield size, formats generated source, and writes `properties_gen.go`.

## Control Flow
The generator uses `go/packages` to inspect syntax and type info, walks type declarations until it finds `github.com/cockroachdb/pebble/sstable.Properties`, records tagged fields in declaration order, locates the package directory, executes the template, formats it, and writes the output file. If formatting fails, it writes the unformatted buffer for debugging before fatal exit.

## State and Persistence Behavior
The generator writes generated Go source to the `sstable` package. Generated code persists property load-state in a `Loaded` bitfield and encodes properties into maps for row/columnar property blocks.

## Dependencies and Integration Points
Triggered by `//go:generate` in `properties.go`. Depends on `go/ast`, `go/packages`, `reflect.StructTag`, `text/template`, and `go/format`. Generated code is consumed by `Properties` load/save/string paths.

## Risks and Edge Cases
Only bool, uint8, uint32, uint64, and string property fields are supported. More than 64 tagged fields fails due to the `Loaded` bitfield. Template imports must stay gofmt-compatible. Adding tags/options requires generator support.

## Test Signals
No direct test in this subset; correctness is checked indirectly by compiling generated code and by properties read/write tests.
