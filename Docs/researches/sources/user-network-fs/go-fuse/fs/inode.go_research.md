# sources/user-network-fs/go-fuse/fs/inode.go

Purpose: defines the in-memory inode model, stable attributes, tree links, locking helpers, lifecycle/removal, and cache notification methods.

Important APIs/types/functions: `StableAttr` with immutable mode/ino/gen and `Reserved`; `Inode` fields for ops, bridge, node ID, open files, backing IDs, persistent flag, change counter, lookup count, children, and parents; locking helpers `lockNodes`; lifecycle `NewInode`, `NewPersistentInode`, `ForgetPersistent`, `removeRef`; tree operations `GetChild`, `AddChild`, `RmChild`, `MvChild`, `ExchangeChild`, `Path`; notification/cache APIs `NotifyEntry`, `NotifyPrune`, `NotifyDelete`, `NotifyContent`, `WriteCache`, `ReadCache`.

Control flow/state: inode liveness depends on lookup count, persistence, children, and parents. Lock ordering by address prevents deadlocks for multi-inode operations. Removal can cascade to unused parents and call `OnForget`.

Risks/test signals: concurrency and lifecycle correctness are critical. Risks include stale paths for orphaned nodes, parent selection for hard links, change-counter retry logic, and notification server availability. Tests cover `IsDir`, parent storage, forget callbacks, rename/exchange, deleted paths, and cache notifications.
