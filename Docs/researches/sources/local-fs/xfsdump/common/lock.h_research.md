# File Research: sources/local-fs/xfsdump/common/lock.h

## Role

This header declares the global critical-region lock API.

## API

- `lock_init()`
- `lock()`
- `unlock()`

It is used by shared components such as stream tracking to serialize updates without exposing the underlying `qlock` implementation.
