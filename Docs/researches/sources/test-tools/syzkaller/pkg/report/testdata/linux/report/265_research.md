<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265

## Purpose
This fixture verifies soft-lockup parsing in ALSA raw MIDI writes. The expected title is `BUG: soft lockup in snd_rawmidi_write`, alternate `stall in snd_rawmidi_write`, type `HANG`, and `PANICKED: Y`.

## Important APIs, Types, and Functions
The raw log contains a watchdog soft lockup, panic, and later RCU stall output. Parser paths include soft-lockup matching, hang alt generation, panic detection, and report-boundary handling. Key symbols include `_raw_spin_unlock_irqrestore`, `snd_virmidi_output_trigger`, `snd_rawmidi_kernel_write1`, `snd_rawmidi_write`, `__vfs_write`, `vfs_write`, `ksys_write`, `SyS_write`, `watchdog_timer_fn.cold.5`, and printk/console functions.

## Control Flow
The reporter must take the first soft-lockup report, select `snd_rawmidi_write` from the stalled task stack, record the panic, and not let the later RCU stall or console printing stack retitle the report.

## State and Persistence Behavior
The fixture persists a 153-line mixed softlockup/RCU/panic log. Expected state is the HANG title, alt, and panic flag.

## Dependencies and Integration Points
It depends on Linux watchdog soft-lockup regexes, stack parser skip lists, panic detection, and hang classification.

## Risks and Edge Cases
The log includes secondary RCU stall diagnostics after the panic, which can look like another hang report. The parser must preserve first-crash semantics.

## Test Signals
Stable parse returns `BUG: soft lockup in snd_rawmidi_write`, alt `stall in snd_rawmidi_write`, type `HANG`, and `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/265 -->
