# sources/test-tools/syzkaller/tools/syz-upgrade/upgrade.go

## Purpose

`upgrade.go` rewrites a syzkaller corpus directory from an older program serialization format to the current one. It is a manual migration helper used while changing `prog.Serialize` and `prog.Deserialize`.

## Important APIs, Types, and Functions

The file defines `main` and `fatalf`. `main` uses `prog.GetTarget(runtime.GOOS, runtime.GOARCH)`, `target.Deserialize(data, prog.NonStrict)`, `p.Serialize`, SHA-1 hashing, `osutil.WriteFile`, and `os.Remove`.

## Control Flow

The tool expects a single corpus directory. It reads each directory entry, deserializes the program non-strictly, serializes it with current code, and compares bytes. Changed programs are printed, written under the SHA-1 hash of the new serialization, and the old file is removed.

## State and Persistence Behavior

This tool mutates the corpus directory in place and can delete original files after successful replacement. It does not recurse into subdirectories and stops on the first fatal error.

## Dependencies and Integration Points

It depends on local runtime GOOS/GOARCH target descriptions and syzkaller program serialization semantics. It is part of developer workflow around corpus format changes.

## Risks and Test Signals

The operation is destructive and assumes the current runtime target matches the corpus target. Hash-based filenames can collide only cryptographically improbably, but existing files with the same hash may be overwritten by `osutil.WriteFile` semantics. Tests should use a temporary corpus, verify unchanged files remain, changed files are renamed to content hash, and malformed programs abort.
