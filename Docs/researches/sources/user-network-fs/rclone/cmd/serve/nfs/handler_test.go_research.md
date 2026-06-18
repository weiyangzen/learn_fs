# sources/user-network-fs/rclone/cmd/serve/nfs/handler_test.go

## Purpose

This file tests NFS mount-path handling and subpath filesystem behavior.

## Important APIs, Types, and Functions

`newTestHandler` builds a local VFS with `/sub`, `/sub/nested`, and `/sub/hello.txt`. Tests include root mount, subpath mount, rejected mounts, subpath writes, and handle stability.

## Control Flow

Tests call `Handler.Mount` with raw dirpaths, inspect returned `*FS` roots, list subpath contents, write through a subpath FS, verify the write lands under the absolute VFS path, and compare root/subpath NFS handles.

## State and Persistence Behavior

Each test uses a temp local filesystem with VFS cache mode full and shuts down VFS at cleanup.

## Dependencies and Integration Points

It depends on local backend, VFS, go-nfs mount request/status types, and the cache path-rewriter.

## Risks and Test Signals

These tests directly protect traversal normalization, non-directory rejection, non-nil rejected FS behavior, and subpath handle identity. They do not run a full network NFS client.
