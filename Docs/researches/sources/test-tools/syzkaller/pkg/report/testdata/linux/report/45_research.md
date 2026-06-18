# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/45

Purpose: golden fixture for ARM64 paging-request parsing in ALSA timer teardown. Expected title is `BUG: unable to handle kernel paging request in _snd_timer_stop`, alternate title is `bad-access in _snd_timer_stop`, type is `MEMORY_SAFETY_BUG`, and `CORRUPTED: Y`.

Important APIs, types, and functions: parser fields include `Corrupted` and memory-safety crash typing. Kernel frames are represented in ARM64 style with `PC is at _snd_timer_stop.constprop.9+0x184/0x2b0`, `LR is at` the same function, and register/state lines.

Control flow: after headers, the log reports lock debugging disabled by taint, a bad virtual address `dead000000000108`, page table state, internal oops, and an ARM64 PC/LR crash location. The parser must extract the title from `PC is at` formatting rather than x86 `RIP:`.

State and persistence behavior: static corrupted fixture; `CORRUPTED: Y` records that report extraction should mark the crash as potentially unreliable. No runtime state is updated.

Dependencies and integration points: depends on Linux ARM64 oops parsing, bad-access alternate-title generation, corruption detection, and `crash.TitleToType` mapping to `MEMORY_SAFETY_BUG`.

Risks: architecture-specific format can be missed by x86-only parsing. The `dead...` poison address and taint text are strong signals for corruption and must not suppress the report.

Test signals: `Unable to handle kernel paging request`, address `dead000000000108`, `Internal error: Oops`, `PC is at _snd_timer_stop.constprop.9`, and corrupted expectation header.
