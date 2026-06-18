<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341

## Purpose
This small fixture checks a corrupted generic warning with panic-on-warn. The expected title is `WARNING in corrupted`, type `WARNING`, with corrupted and panicked flags.

## Important APIs, Types, And Functions
The visible warning is at `arch/x86/kernel/irq_64.c:61 handle_irq+0x2cb/0x3d8`, followed immediately by `Kernel panic - not syncing: panic_on_warn set ...` and a short call-trace marker.

## Control Flow
The reporter detects the warning but cannot produce a stable non-corrupted function title from the truncated context, then marks the panic state from the panic-on-warn line.

## State And Persistence
State is entirely fixture metadata plus raw log. `CORRUPTED: Y` records the incomplete report body.

## Dependencies And Integration Points
It depends on generic warning recognition, corrupted-title fallback, and panic-on-warn detection.

## Risks
If parser heuristics start trusting the visible `handle_irq` site, the expected `corrupted` title would regress.

## Test Signals
The parse should remain `WARNING in corrupted`, type `WARNING`, `CORRUPTED: Y`, `PANICKED: Y`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/341 -->
