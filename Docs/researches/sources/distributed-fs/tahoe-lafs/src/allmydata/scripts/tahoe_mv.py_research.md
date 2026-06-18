# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mv.py

## Purpose
Implements `tahoe mv` and related move/rename behavior within Tahoe directories by linking the target to an existing child and deleting the original.

## Important APIs, Types, and Functions
`mv(options, mode="move")` is the public command. It uses alias parsing, regex URL splitting, webapi JSON inspection, `PUT ?t=uri` for target creation/linking, and `DELETE` for source removal.

## Control Flow
The command resolves source and destination aliases, rejects cross-rootcap moves, fetches source JSON, determines whether destination denotes a directory by trailing slash or existing JSON node, builds the target URL and child name, prevents overwriting a directory with a file, writes the source URI to the destination with `PUT ?t=uri`, then deletes the original. If delete fails after the put, it returns 2 to signal partial move failure.

## State and Persistence Behavior
Persistence is entirely remote Tahoe directory mutation: target link creation followed by source link deletion. This ordering means delete failure can leave both links present, and the module reports that as a distinct error path.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, `json`, and `encodingutil.to_bytes`. It integrates with Tahoe webapi JSON node metadata and URI-link endpoints.

## Risks and Edge Cases
The move is not atomic because it uses separate PUT and DELETE requests. Cross-alias/rootcap moves are rejected. Existing destination directory handling depends on JSON type inspection and trailing slash semantics. Regex-based parent/name splitting is sensitive to unusual paths.

## Test Signals
`src/allmydata/test/cli/test_mv.py` covers rename, overwrite file, directory collision rejection, trailing-slash move into directory, nested directories, DELETE failure partial error, missing default alias, and nonexistent aliases.
