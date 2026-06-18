# sources/object-store/minio-mc/cmd/find.go

Purpose: Implements matching, listing, watch mode, formatting, external execution, presigned URL substitution, and metadata/tag regex filters for `mc find`.

Important APIs/types/functions: `findMessage`, `nameMatch`, `patternMatch`, `pathMatch`, `getExitStatus`, `execFind`, `watchFind`, `trimSuffixAtMaxDepth`, `getAliasedPath`, `find`, `doFind`, `stringsReplace`, `matchFind`, `getShareURL`, `getRegexMap`, `matchRegexMaps`, and `matchMetadataRegexMaps`.

Control flow: `doFind` recursively lists content, skips selected listing errors and Glacier objects, converts `ClientContent` to `contentMessage`, filters through `matchFind`, then either runs `--exec`, applies `--print`, or prints the path. Watch mode is deferred and consumes put events until cancellation.

State and persistence: Read-only listing/watch except `--exec`, which can run arbitrary user commands. Generates presigned URLs when `{url}` is requested.

Dependencies/integration: Uses `Client.List`, `Client.Watch`, share URL APIs, shlex, wildcard matching, regex, normalization, console, and global context.

Risks: `--exec` exits the whole process on command failure and executes user-provided programs. `doFind` lists with `globalContext` instead of the passed context. Regex map keys are exact/canonicalized only for metadata.

Test signals: `find_test.go` covers matching predicates, max depth trimming, substitution, and exit status extraction.
