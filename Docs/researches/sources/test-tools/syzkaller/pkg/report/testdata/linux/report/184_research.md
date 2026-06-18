<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184

## Purpose
This fixture covers packet-socket list corruption during protocol-hook removal. It expects title `BUG: corrupted list in __dev_remove_pack`, alt `bad-access in __dev_remove_pack`, and type `MEMORY_SAFETY_BUG`. The log is shorter than most neighboring files and centers on `kernel BUG at lib/list_debug.c:56!`.

## Important APIs, Types, And Functions
The file uses the same report-test metadata contract. Parser functions exercised are list-debug BUG detection, title selection from a short stack, alternate bad-access title generation, and memory-safety classification. Kernel frames include `__dev_remove_pack`, `__unregister_prot_hook`, `packet_release`, `packet_rcv_spkt`, `sock_close`, `__fput`, `task_work_run`, `do_exit`, `do_group_exit`, `SYSC_exit_group`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter reads the metadata, then scans the 54-line raw report. The crash path is process exit closing a packet socket; release unregisters a protocol hook and trips list-debug validation in `__dev_remove_pack`. The parser should use the first meaningful frame as the title because there is little secondary context.

## State And Persistence
State is static fixture text. Dynamic addresses and KMSAN-style shadow-origin frames in the log are transient. The persistent expected state is the title, alt, type, and the compact console trace.

## Dependencies And Integration Points
It integrates with Linux list-corruption matchers, packet-socket stack parsing, and syzkaller's report test loader. The fixture broadens coverage beyond TIPC by exercising a networking core packet hook list.

## Risks
Short reports increase the risk that the parser selects `packet_release` or generic list-debug text instead of `__dev_remove_pack`. The source also contains sanitizer helper frames that should not be treated as crash-owner APIs.

## Test Signals
Regression checks should confirm exact title, `MEMORY_SAFETY_BUG`, and alt title. The report should retain `lib/list_debug.c:56` and the `packet_release` to process-exit path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/184 -->
