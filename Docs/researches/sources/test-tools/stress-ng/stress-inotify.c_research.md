# sources/test-tools/stress-ng/stress-inotify.c

## Purpose
`stress-inotify.c` exercises Linux inotify by creating temporary files/directories and verifying event delivery for access, modify, attrib, close, open, move, create, delete, delete-self, and move-self operations. It also probes invalid inotify operations for syscall coverage.

## Important APIs, Types, And Functions
`stress_inotify_t` maps each event helper to a description. `exercise_inotify1()`, `exercise_inotify_add_watch()`, and `exercise_inotify_rm_watch()` cover valid and invalid inotify API calls, masks, watch descriptors, `INOTIFY_IOC_SETNEXTWD`, bad fds, and non-inotify fds. `inotify_exercise()` is the common harness: it creates an inotify fd, adds a watch, invokes a file operation helper, waits with `select()`, checks bytes with `FIONREAD`, reads events, and matches flags/names. Helpers `mk_file`, `mk_dir`, `rm_file`, and `rm_dir` manage test objects.

## Control Flow
`stress_inotify()` creates a temp directory, reports nominal file usage, waits at the sync barrier, then repeatedly walks the `inotify_stressors[]` table. Each concrete event function sets up a scenario, invokes `inotify_exercise()`, and cleans up. The common harness waits up to 10 seconds for expected events and only treats timeouts as failures in verify mode.

## State And Persistence
The stressor creates and removes temporary files/directories under the stress-ng temp directory. Runtime state is fd/watch descriptors and stack event buffers. No persistent files should remain after cleanup.

## Dependencies And Integration Points
Requires glibc 2.9-era inotify APIs, `<sys/inotify.h>`, `select()`, optional epoll for negative tests, stress-ng bad-fd and temp-file helpers, and verify flags.

## Risks
Inotify event coalescing, filesystem latency, queue pressure, or resource limits can cause timeouts or `EMFILE`. Some match names in move helpers are broad, so verification relies on masks as well as names. Negative tests should not accidentally close/remove live descriptors. Cleanup must handle partially completed rename/delete scenarios.

## Test Signals
Run with and without `--verify`, confirm every compiled event helper can complete, observe retry on transient `EMFILE`, validate `FIONREAD` and event parsing, and ensure the temp directory is removed after errors.
