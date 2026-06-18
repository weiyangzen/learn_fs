# sources/security-integrity/fscrypt/util/util.go

Purpose: This file provides low-level fscrypt helpers for unsafe pointer conversion, integer slice lookup, user/group resolution, numeric parsing, mount table scanning, path checks, and filesystem-related utilities.

Important APIs and functions: `Ptr`, `ByteSlice`, and `PointerSlice` bridge Go slices and raw pointers for syscall/cgo-style code. `Index`/`Lookup` provide simple table lookup. The user/group helpers parse ids or names and normalize current user information. Other helpers cover line scanning, device/mount metadata, and system calls through `golang.org/x/sys/unix`.

Control flow and state: Most helpers are stateless wrappers that validate input and return derived data or errors. Unsafe slice views intentionally do not own memory and depend on caller lifetime guarantees.

Dependencies and integration points: Integrated across fscrypt packages that invoke kernel ioctls, inspect mountpoints, and resolve users. Depends on `bufio`, `os/user`, `strconv`, `unsafe`, and `unix`.

Risks and test signals: Unsafe pointer helpers are high-risk if callers index beyond valid backing memory. User and mount helpers can vary across OS/user database environments. Tests should target empty-slice pointer behavior, lookup misses, numeric parse errors, and system-call error wrapping.
