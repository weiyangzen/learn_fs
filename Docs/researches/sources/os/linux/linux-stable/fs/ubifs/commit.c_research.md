# File Research: sources/os/linux/linux-stable/fs/ubifs/commit.c

Purpose: Manages UBIFS commit execution, background commit thread behavior, commit state transitions, and old-index debug checking.

Key responsibilities:
- Detects when there is nothing to commit by checking mounting/remount state, dirty TNC root, dirty LPT nodes, and dirty counters.
- Implements two-phase commit: a short exclusive start phase under `commit_sem`, then a longer end phase after releasing it.
- Syncs journal write buffers, starts GC/log/TNC/LPT/orphan commit components, updates master node fields, ends and post-processes commit components.
- Maintains commit state machine: resting, background requested/running, required/running required, and broken.
- Runs background thread work for write-buffer sync and background commits.
- Provides APIs to require a commit, request background commit, run or wait for commit, and let GC escalate background commit to required.
- On commit failure, marks commit broken and switches UBIFS to read-only error mode.
- Includes debug helpers to record and verify the old on-flash index remains intact across commit.

Important interactions:
- Coordinates UBIFS modules: GC, log, TNC, LPT, orphan handling, master node, write buffers, and debug checks.
- Uses `commit_sem`, `cs_lock`, `cmt_wq`, freezer-aware kthread behavior, and UBIFS read-only error handling.

Notable invariants and risks:
- Commit start must minimize I/O while holding exclusive journal access to avoid latency spikes.
- The old index must remain recoverable until the new committed state is durable.
- Background and foreground commit paths race through a shared state machine; transitions carefully upgrade background work to required commits when needed.
