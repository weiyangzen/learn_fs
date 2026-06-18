# File Research: sources/virtualization/qemu/block/blkdebug.c

This file implements the `blkdebug` block filter/protocol for deterministic error injection, state transitions, breakpoints, request suspension, and block-limit override testing.

Key state:
- `BDRVBlkdebugState` stores fixed limit overrides, config filename, child permission modifiers, current state, per-event rules, active injected-error rules, suspended requests, and a mutex.
- `BlkdebugRule` describes one event/action: inject error, set state, or suspend.
- `BlkdebugSuspendedReq` tracks a yielded coroutine and tag for later resume.

Configuration:
- `inject-error` options support event, state, I/O type mask, errno, sector offset, once/immediately behavior, and delay.
- `set-state` options support event, state, and new state.
- Runtime options include `config`, internal `x-image`, alignment and max-transfer overrides, write-zero/discard alignments and maximums.
- `read_config()` parses both config file and QDict-provided rules, then resets global `QemuOptsList` state.

Open and limits:
- `blkdebug_parse_filename()` accepts `blkdebug:config:image` and maps it to `config` and `x-image`.
- `blkdebug_open()` initializes lock, reads rules, parses child permission modifiers, opens the image child, mirrors supported write/zero flags, validates override limits, and triggers `BLKDBG_NONE`.
- `blkdebug_refresh_limits()` applies configured overrides to `bs->bl`.
- `blkdebug_child_perm()` applies default permissions plus explicit take/unshare permission modifiers.

I/O behavior:
- `rule_check()` scans active injected-error rules for matching offset and I/O type, optionally removes one-shot rules, sleeps for configured delay, optionally yields once, and returns `-errno`.
- Read, write, flush, write-zeroes, discard, and block-status handlers check rules before delegating to the child.
- Handlers assert that block-layer alignment and maximum request guarantees are being honored.

Debug events and suspension:
- `blkdebug_co_debug_event()` processes all rules for an event under lock, updates state, activates injected errors, or suspends requests.
- `suspend_request()` records the current coroutine and removes the suspend rule.
- `blkdebug_debug_breakpoint()`, `blkdebug_debug_resume()`, `blkdebug_debug_remove_breakpoint()`, and `blkdebug_debug_is_suspended()` implement breakpoint management by tag.
- `resume_req_by_tag()` temporarily drops the mutex while entering the suspended coroutine.

Filesystem/block relevance:
- `blkdebug` is a test-oriented block filter that exercises error paths and block-limit handling in upper layers and image drivers.
- It is especially useful for filesystem/block-stack reliability testing because it can inject failures at precise block events and request types.

Potential pitfalls:
- Rule storage is protected by a mutex, but callbacks can enter coroutines while lock is temporarily dropped.
- `remove_rule()` assumes the rule is linked in its event list.
- `blkdebug` is intentionally invasive and should be viewed as a test harness, not a production storage backend.
