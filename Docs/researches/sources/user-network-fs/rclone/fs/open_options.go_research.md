# sources/user-network-fs/rclone/fs/open_options.go

## Purpose
`open_options.go` defines rclone's generic open/read options. These options let callers request HTTP ranges, seek offsets, extra HTTP headers, hash calculation limits, metadata injection, no-op placeholders, and preferred chunks.

## Important APIs, types, and functions
Core exports are `OpenOption`, `RangeOption`, `ParseRangeOption`, `RangeOption.Decode`, `FixRangeOption`, `SeekOption`, `ParseHeaders`, `MustParseHeaders`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `MetadataAsOpenOptions`, `ChunkOption`, `OpenOptionAddHeaders`, `OpenOptionHeaders`, and `OpenOptionAddHTTPHeaders`.

## Control flow
Options expose `Header`, `String`, and `Mandatory`. `RangeOption.Header` renders RFC 7233 byte ranges; `ParseRangeOption` accepts only a single `bytes=` range; `Decode` converts inclusive ranges into offset/limit. `FixRangeOption` normalizes suffix ranges and seeks into absolute ranges when size is known, caps end offsets, and replaces ranges on zero-size files with `NullOption`. Header helpers collect non-empty option headers into maps or `http.Header`.

## State and persistence behavior
Options are plain values/slices. `FixRangeOption` mutates the supplied slice in place and may replace option objects. `MetadataAsOpenOptions` reads context config and returns metadata-set options.

## Dependencies and integration points
Backends inspect open options in `Object.Open` and upload/update methods. HTTP backends use header helpers. Local hashing uses `HashesOption`; metadata copy paths use `MetadataOption`; multipart/upload code can use `ChunkOption`.

## Risks and edge cases
Range end is inclusive, while `Decode` returns a count. `FixRangeOption` cannot normalize unknown-size objects. Suffix ranges with `End` greater than size can produce negative starts before later capping if callers pass unusual data. Multiple HTTP ranges are explicitly unsupported. `MustParseHeaders` fatal-exits on bad user input.

## Test signals
`open_options_test.go` covers range parsing errors and variants, decode math, string/header/mandatory methods for all option types, range fixing for zero/unknown/known sizes, seek conversion, and map/header construction.

Source-read signal: reviewed complete local file (368 lines). Types observed: `OpenOption`, `RangeOption`, `SeekOption`, `HTTPOption`, `HashesOption`, `NullOption`, `MetadataOption`, `ChunkOption`. Functions/methods observed: `Header`, `ParseRangeOption`, `String`, `Mandatory`, `Decode`, `FixRangeOption`, `Header`, `String`, `Mandatory`, `ParseHeaders`, `MustParseHeaders`, `Header`, `String`, `Mandatory`, `Header`, `String`.
