<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift.go -->
# sources/sync-backup/restic/internal/backend/swift/swift.go

## Purpose
Implements the OpenStack Swift object storage backend.

## Important APIs, Types, And Functions
beSwift, NewFactory, Open, IsNotExist/IsPermanentError, Properties, Hasher, Save, Load/openReader, Stat, Remove, List, Delete, Close, Warmup/WarmupWait, and path helpers are central.

## Control Flow
Open builds a swift.Connection from config, authenticates, ensures the container exists, and sets DefaultLayout over the prefix. Save uploads bytes with content length and MD5 hash. Load uses ranged ObjectOpen, Stat reads object metadata, List pages objects by layout prefix, Remove deletes objects, and Delete removes all keys under the layout.

## State And Persistence Behavior
Repository state is persisted as Swift objects in a container/prefix. Local state is authenticated connection, container, prefix, connection count, and layout.

## Dependencies And Integration Points
Depends on ncw/swift/v2, crypto/md5, backend/layout/location/util, feature flags, errors/debug.

## Risks And Edge Cases
Risks include auth mode complexity, object listing pagination, range/short-read classification, hash mismatch, and container policy behavior.

## Test Signals
swift_test.go runs integration suite when Swift environment variables are available; config tests cover parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift.go -->
