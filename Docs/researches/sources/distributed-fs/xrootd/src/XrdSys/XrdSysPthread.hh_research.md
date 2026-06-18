# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.hh

Purpose: provides XRootD's common synchronization and thread utility wrappers over pthread APIs.

Important APIs/types/functions: declares `XrdSysCondVar`, `XrdSysCondVarHelper`, `XrdSysMutex`, `XrdSysRecMutex`, `XrdSysMutexHelper`, `XrdSysCondVar2`, `XrdSysRWLock`, `XrdSysRWLockHelper`, `XrdSysFusedMutex`, `XrdSysSemaphore`, and static `XrdSysThread`. Thread options are `XRDSYSTHREAD_BIND` and `XRDSYSTHREAD_HOLD`.

Control flow: RAII helper classes lock in constructors or `Lock()` and unlock in destructors. `XrdSysCondVar` optionally owns its mutex depending on `relMutex`; `XrdSysCondVar2` uses a caller-provided mutex. `XrdSysRWLock` wraps read/write locking with optional writer preference on glibc/uClibc. `XrdSysFusedMutex` dispatches to either mutex or rwlock based on construction. `XrdSysSemaphore` uses native semaphores except on Apple/GNU, where the `.cc` condition-variable implementation is used.

State and persistence: objects own pthread mutex/cond/rwlock/semaphore handles. `XrdSysThread` is effectively static and holds only global debug route and stack-size configuration.

Dependencies and integration: includes pthread, signal, semaphore, and Apple clock compatibility code. It is used across XrdSys, XrdOuc, and XrdThrottle for locking, condition signaling, and thread creation.

Risks: wrappers throw string literals or abort in some low-level failure paths rather than returning errors. Some constructors do not check pthread initialization failures. `XrdSysCondVar::Signal()` optionally locks internally only when `relMutex` is set, so callers must match the selected locking model. The glibc writer-preference constructor does not explicitly initialize the rwlock attribute object before setting kind.

Test signals: compile matrix across Linux, macOS, and Windows compatibility branches; stress mutex helpers for double-lock replacement; validate timed locks and timed condition waits; and run thread sanitizer style tests around shared/exclusive lock usage.
