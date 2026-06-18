# Research: sources/user-network-fs/rclone/fs/operations/rc.go

## sources/user-network-fs/rclone/fs/operations/rc.go

Purpose: registers remote-control endpoints that expose `fs/operations` behavior as `rc.Call`s. It wires `operations/list`, `stat`, `about`, `copyfile`, `movefile`, single-command mutators, `size`, `publiclink`, `fsinfo`, `backend/command`, `core/du`, `check`, `hashsum`, and `hashsumfile`. Important functions are `rcList`, `rcStat`, `rcAbout`, `rcMoveOrCopyFile`, `rcSingleCommand`, `rcSize`, `rcPublicLink`, `rcFsInfo`, `rcBackend`, `rcDu`, `rcCheck`, `parseHashParameters`, `rcHashsum`, and `rcHashsumFile`.

Control flow mostly parses `rc.Params`, resolves filesystems with `rc.GetFs*`, delegates to operations functions, and shapes results into `rc.Params`. Multipart upload streams request parts into `Rcat`; check/hash endpoints capture writer output into string slices. There is no durable state except remote filesystem mutations and uploaded data. Dependencies include rc cache helpers, config cache-dir, hash parsing, disk usage, HTTP/multipart parsing, and backend feature methods. Risks include parameter validation drift from CLI behavior, feature nil checks, closure capture in registration loops, upload path joining, partial report defaults in `rcCheck`, and unsupported hash/backend paths. Tests in `rc_test.go` cover most endpoint contracts.
