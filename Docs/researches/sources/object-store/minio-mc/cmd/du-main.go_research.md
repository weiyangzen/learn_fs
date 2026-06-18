# sources/object-store/minio-mc/cmd/du-main.go

Purpose: Implements `mc du`, summarizing object counts and sizes for folders/prefixes.

Important APIs/types/functions: `duFlags`, `duCmd`, `duMessage`, `du`, and `mainDu`.

Control flow: `mainDu` validates arguments, sets depth based on `--depth` and `--recursive`, parses rewind/version flags, verifies each target is a directory, and calls recursive `du`. `du` expands aliases, creates a client, lists with optional versions/time reference, recursively descends into subdirectories when depth allows, skips delete markers/directories, and prints totals.

State and persistence: Read-only listing. No local persistence.

Dependencies/integration: Uses `newClientFromAlias`, `Client.List`, `parseRewindFlag`, `isAliasURLDir`, `humanize`, and console/json output.

Risks: Recursive calls can be expensive for deep trees. Some filesystem errors are skipped while others abort. Prefix handling depends on path cleaning and URL parsing.

Test signals: No direct tests.
