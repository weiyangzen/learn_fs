# `sources/user-network-fs/go-fuse/fuse/pathfs/prefixfs.go`

## Purpose
Implements `NewPrefixFileSystem`, a decorator that prepends a fixed path prefix to all pathfs operations.

## Important APIs, Types, And Functions
`prefixFileSystem` forwards every `FileSystem` method after `filepath.Join(Prefix, name)`, including xattrs, create/open, metadata, links, statfs, mount hooks, and debug toggling.

## Control Flow
`prefixFileSystem` forwards every `FileSystem` method after `filepath.Join(Prefix, name)`, including xattrs, create/open, metadata, links, statfs, mount hooks, and debug toggling.

## State And Persistence
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.

## Test Signals
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.
