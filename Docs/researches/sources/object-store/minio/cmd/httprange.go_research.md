# sources/object-store/minio/cmd/httprange.go

## Purpose

`httprange.go` parses and renders the S3-supported subset of HTTP `Range` headers for object GET requests. It converts string forms such as `bytes=1-10`, `bytes=10-`, and `bytes=-30` into an `HTTPRangeSpec`, then computes concrete object offsets and lengths for a known resource size.

## Important APIs, Types, And Control Flow

`HTTPRangeSpec` has `IsSuffixLength`, `Start`, and `End`. A nil spec means no Range header and therefore the full resource. For suffix ranges, `Start` is stored as a negative length and `End` is `-1`. `GetLength(resourceSize)` validates negative resource sizes, handles nil/full-object ranges, clamps suffix ranges to resource size, rejects starts beyond the resource with `InvalidRange`, clamps explicit end offsets past EOF, and computes inclusive byte counts. `GetOffsetLength` calls `GetLength`, then returns start offset plus length, converting suffix ranges with `max(resourceSize + Start, 0)`.

`parseRequestRangeSpec` requires the `bytes=` prefix, rejects missing `-`, rejects signed byte positions with a leading `+`, parses begin/end as non-negative integers, rejects multi-range strings because S3/MinIO does not support RFC multi-ranges here, and returns `errInvalidRange` for syntactically valid but unsatisfiable or reversed ranges. `String(resourceSize)` renders the concrete inclusive range after resource-size clamping. `ToHeader` reconstructs the original header shape and validates reversed or malformed specs.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state; the type is a pure request parser used by object GET/range handling. Dependencies are only `errors`, `fmt`, `strconv`, and `strings`, plus package-level `InvalidRange` and `errInvalidRange`. Risks include unsupported multi-range behavior, `ToHeader` converting `int64` through `int` before string conversion on narrow architectures, subtle distinction between parse errors and invalid-range errors, and nil specs needing careful handling by callers. `httprange_test.go` covers valid offsets, suffix clamping, parse failures, invalid range classification, and round-tripping with `ToHeader`.
