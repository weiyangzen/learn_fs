# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/755`. It records expected title `WARNING in ext4_xattr_inode_update_ref` and covers ext4 xattr inode reference warning during inode eviction. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in ext4_xattr_inode_update_ref`, type `WARNING`, frame `ext4_xattr_inode_update_ref`, alternate titles none, flags `none`, executor `proc=0, id=17`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `ext4_xattr_inode_iget`
- `ext4_xattr_set_entry`
- `ext4_xattr_ibody_set`
- `ext4_expand_extra_isize_ea`
- `__ext4_expand_extra_isize`
- `__ext4_mark_inode_dirty`
- `ext4_evict_inode`
- `do_raw_spin_unlock`
- `evict`
- `_raw_spin_unlock`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 76 total lines, 71 log lines, 0 expected report lines, and 4963 bytes. Salient log lines include:

- [   92.524882][ T5982] WARNING: fs/ext4/xattr.c:1058 at 0x0, CPU#0: syz.0.17/5982

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
