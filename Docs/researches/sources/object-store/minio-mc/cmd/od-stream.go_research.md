# Research: sources/object-store/minio-mc/cmd/od-stream.go

## sources/object-store/minio-mc/cmd/od-stream.go

Purpose: contains the transfer mechanics for `mc od`, including part-size math, copy/upload timing, and S3 part download composition.

Important APIs and functions: `odSetSizes` calculates combined size, part size, part count, and byte skip; `odCopy` uploads a selected range or generated stream to a target; `odSetParts` validates download part controls; `odDownload` writes S3 content to a local target; `singleGet` and `multiGet` obtain one or many object parts.

Control flow: uploads calculate size/skip, open a source stream with optional range start, create `PutOptions`, disable multipart for small known sizes, count bytes with an accounter, call `PutPart`, and return an `odMessage`. Downloads choose full-object or multipart reads, then pipe them to `putTargetStream`.

State and persistence: reads source data and writes target data. Uses no local persistent state.

Dependencies and integration: uses `Client.GetPart`, `Client.PutPart`, `getSourceStreamFromURL`, `putTargetStream`, `newAccounter`, `PutOptions`, and human-readable byte parsing.

Risks and tests: `multiGet` loops from `1 + skip` to `parts` but calls `cli.GetPart(ctx, parts)` instead of the loop index, which looks suspicious. Division by `partSize` occurs when building `Skip`. There are no direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/od-stream.go -->
