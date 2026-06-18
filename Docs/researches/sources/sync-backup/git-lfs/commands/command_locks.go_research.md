<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_locks.go -->
# sources/sync-backup/git-lfs/commands/command_locks.go

Purpose: implements `git lfs locks`, listing local, cached, remote, filtered, or verification-classified locks in text or JSON form.

Important APIs/types/functions: global `locksCmdFlags`; `locksCommand`; `locksFlags` with `Filters`; `locking.Client.SearchLocks`, `SearchLocksVerifiable`, `EncodeLocks`, and `EncodeLocksVerifiable`.

Control flow: computes lock path filters, applies optional remote override, builds lock client with current remote ref, validates incompatible `--cached` and `--verify` combinations, queries locks or verifiable own/their lock sets, writes JSON if requested, otherwise sorts by path and prints padded rows with optional ownership marker. Retrieval errors are reported after printing any partial results.

State and persistence behavior: may read/write local lock cache depending on client query mode; remote queries contact locking API. Text formatting is derived from returned lock owner fields.

Dependencies/integration points: shares path normalization with `lock`, JSON flag state with lock/unlock, and remote/ref setup with lock client. Verification mode supports pre-push lock semantics.

Risks and test signals: risks include using `locking.Lock` as a map key, partial output before final error, incompatible flag matrix, and cached/local semantics diverging from remote truth. Test signals include path/id filters, limits, local-only, cached-only, verify mode, JSON encoders, sorting/padding, and server errors with partial data.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_locks.go -->
