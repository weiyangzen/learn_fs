<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261

## Purpose
This fixture verifies KASAN use-after-free write parsing for ALSA timer callbacks. The expected title is `KASAN: use-after-free Write in snd_timer_user_interrupt`, alt `bad-access in snd_timer_user_interrupt`, and type `KASAN-USE-AFTER-FREE-WRITE`.

## Important APIs, Types, and Functions
The source uses `TITLE`, `ALT`, and `TYPE` headers. Parser paths include KASAN report matching, access kind extraction, stack classification, and alternate bad-access generation. Important symbols include `register_lock_class`, `kasan_report.cold.6`, `__asan_report_store8_noabort`, `__lock_acquire`, `snd_seq_check_queue.part.4`, `snd_timer_user_interrupt`, `snd_timer_interrupt`, `snd_hrtimer_callback`, and hrtimer/APIC frames.

## Control Flow
The reporter starts from `BUG: KASAN: use-after-free in register_lock_class`, then uses the stack and KASAN write metadata to identify the relevant ALSA timer user interrupt frame. It must ignore generic lock-class registration frames in the report headline.

## State and Persistence Behavior
The file persists one KASAN crash report with expected title, alt, and type. It has no mutable state.

## Dependencies and Integration Points
It depends on KASAN parser rules, write/read access typing, frame skip lists, and crash type mapping.

## Risks and Edge Cases
The textual KASAN headline names `register_lock_class`, while the expected syzkaller title names `snd_timer_user_interrupt`; parser frame selection is therefore the critical behavior under test.

## Test Signals
The output must be the ALSA timer title, alt `bad-access in snd_timer_user_interrupt`, and type `KASAN-USE-AFTER-FREE-WRITE`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/261 -->
