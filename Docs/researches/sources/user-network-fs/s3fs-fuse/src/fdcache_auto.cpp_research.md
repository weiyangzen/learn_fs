# sources/user-network-fs/s3fs-fuse/src/fdcache_auto.cpp

Purpose: Implements `AutoFdEntity`, an RAII helper that pairs a raw `FdEntity*` with its pseudo-fd and automatically closes it through `FdManager`.

Important APIs and functions: Constructor initializes empty state. Destructor calls `Close`. `Close` delegates to `FdManager::Close` and clears local state. `Detach` transfers pseudo-fd ownership to the caller without closing. `Attach` binds to an existing pseudo-fd without creating a new one. `Open`, `GetExistFdEntity`, and `OpenExistFdEntity` wrap the corresponding `FdManager` APIs.

Control flow: Before every attach/open operation, `Close` releases any previous association. `Open` initializes `pseudo_fd` to `-EIO` before calling `FdManager::Open` so early failure paths can still return a meaningful negative error through the optional `error` pointer. `GetExistFdEntity` intentionally returns an entity without storing it in the RAII state because it does not create a new pseudo-fd.

State and persistence behavior: Stores only `pFdEntity` and `pseudo_fd`; it owns no on-disk state. Persistence effects come from the manager/entity close path, which may serialize page stats and release cache/mirror descriptors.

Dependencies and integration points: Depends on `fdcache.h` and logger macros. Used by s3fs FUSE operations to keep entity reference counts balanced across early returns.

Risks: `Detach` disables automatic close and must be used only when the caller will later close the pseudo-fd. `GetExistFdEntity` returns a raw entity while leaving `pFdEntity` null, so code must not assume all returned entities are RAII-owned. If `FdManager::Close` fails, `Close` leaves state uncleared to surface the problem.

Test signals: Open/close leak tests are indirect; relevant integration signals are multi-open, release, flush, and error-path tests. The explicit `-EIO` initialization is a regression guard for early `FdManager::Open` failures returning useful errors.
