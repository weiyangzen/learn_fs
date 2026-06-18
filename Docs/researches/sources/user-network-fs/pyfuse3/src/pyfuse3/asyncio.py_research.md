# sources/user-network-fs/pyfuse3/src/pyfuse3/asyncio.py

Purpose: Provides an asyncio compatibility shim that makes pyfuse3's internals see an object shaped enough like Trio for asyncio-based operation loops.

Important APIs/types/functions: `enable` replaces `pyfuse3.trio` with this module and aliases `lowlevel`/`from_thread`. `disable` restores real Trio. `Lock` aliases `asyncio.Lock`. `wait_readable`, `notify_closing`, `current_task`, `_Nursery`, and `open_nursery` emulate the subset of Trio low-level APIs that pyfuse3 uses.

Control flow: `wait_readable` registers a loop reader for a file descriptor, waits on a future, removes the reader on completion, and tracks waiters in `_read_futures`. `notify_closing` fails outstanding futures with `ClosedResourceError`. `_Nursery` collects tasks created by `start_soon` and waits for all on context exit.

State and persistence: `_read_futures` is process-global fd-to-future-set state. `_Nursery.tasks` is per-context state. No data persists beyond process lifetime.

Dependencies and integration points: Depends on `asyncio`, `sys`, and pyfuse3's `trio` module variable. Example `hello_asyncio.py` and users can switch pyfuse3 to asyncio mode.

Risks: This is a compatibility subset, not a full Trio implementation. `_Nursery.__aexit__` waits for task completion but does not implement Trio-like cancellation semantics. `notify_closing` indexes `_read_futures[fd]`, which creates an empty set for unknown fds.

Test signals: `test_examples.py` parametrizes `hello.py` and `hello_asyncio.py`, giving end-to-end coverage that the shim can run a mounted example.
