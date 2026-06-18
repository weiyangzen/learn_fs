# sources/user-network-fs/rclone/backend/cache/handle.go

## Purpose
`handle.go` implements read handles for cached objects and the background upload worker for temp-write mode. It is the cache backend's main streaming and asynchronous upload control surface.

## Important APIs, Types, And Control Flow
`NewObjectHandle` creates a `Handle`, in-memory chunk cache, preload queue, worker pool, and starts read workers. `Read` calls `getChunk` at the current offset and copies bytes to the caller. `Seek` adjusts the current offset and preloads nearby chunks. Workers read offsets from `preloadQueue`, reuse range-capable readers when possible, fetch missing chunks from the wrapped object, then write chunks to memory and persistent storage. Plex integration initially limits workers to one and scales out when external playback is confirmed. The background upload path uses singleton `backgroundWriter` instances by cache FS string. `run` polls `Persistent.getPendingUpload`, moves files from temp FS to wrapped FS, cleans empty temp dirs, removes pending records, expires parent cache, emits change notification, and publishes upload state.

## State And Persistence
Read state includes current offset, seen chunk offsets, worker count, queue, transient memory cache, and persistent chunk files. Background upload state is in the Bolt pending bucket, temp filesystem files, `notifyCh`, and `running` flags protected by mutexes. Persistent chunks are stored under the object's absolute path with offset filenames.

## Dependencies And Integration Points
It depends on cache `Memory` and `Persistent`, `fs.RangeOption`/`RangeSeeker`, `operations.MoveFile`, Plex connector state, the wrapped object `Open`, temp FS features, and upstream notifications. It implements `io.ReadCloser` and `io.Seeker`.

## Risks And Test Signals
Risks include goroutine coordination around queue close and scale-in sentinels, range-reader reuse after errors, chunk retry timing, memory eviction by offset, persistent chunk races, background upload singleton lifecycle, and started-upload operations. Upload tests validate queue behavior, started/completed/error notifications, temp cleanup, and blocked mutations. Internal cache tests validate chunk size limits and cached read correctness.
