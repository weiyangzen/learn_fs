<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183

## Purpose
This fixture validates list-corruption recognition in TIPC subscription teardown. It expects title `BUG: corrupted list in tipc_nametbl_unsubscribe`, alternate `bad-access in tipc_nametbl_unsubscribe`, and type `MEMORY_SAFETY_BUG`. The log contains `list_del corruption` followed by `kernel BUG at lib/list_debug.c:53!`.

## Important APIs, Types, And Functions
The file is report-test data with `TITLE`, `ALT`, and `TYPE` headers. Parser features under test include list-debug BUG parsing, invalid-op handling, corrupted-list title normalization, and stack-frame selection. Important frames include `__list_del_entry_valid`, `tipc_nametbl_unsubscribe`, `tipc_subscrb_subscrp_delete`, `tipc_subscrb_release_cb`, `tipc_close_conn`, `tipc_topsrv_kern_unsubscr`, `tipc_group_delete`, `tipc_sk_leave`, `tipc_release`, `sock_release`, `__fput`, `do_exit`, and `entry_SYSCALL_64_fastpath`.

## Control Flow
The reporter should identify the list debug message as the crash start, skip generic `__list_del_entry_valid` naming, and select `tipc_nametbl_unsubscribe` from the meaningful call stack. The execution path is user-triggered TIPC socket or group cleanup, descending through subscription deletion and socket release during exit/task-work processing.

## State And Persistence
Persistent expected state is the metadata and 140-line log. Volatile runtime state includes list pointer values, stack addresses, socket state, and PIDs. There is no persistence outside the test fixture; the source file itself is the golden parser input.

## Dependencies And Integration Points
This fixture depends on syzkaller's Linux list-corruption recognizers, bad-access alternate-title generation, TIPC stack parsing, and memory-safety type classification. It is consumed by the common report parser tests for Linux target data.

## Risks
A regression could emit `kernel BUG in __list_del_entry_valid` rather than the TIPC function, or classify the issue as a generic crash instead of `MEMORY_SAFETY_BUG`. Another risk is losing the alternate bad-access title for list corruption.

## Test Signals
Check for exact title, alt title, and type. The selected report should contain `list_del corruption`, `lib/list_debug.c:53`, and the `tipc_nametbl_unsubscribe` frame before generic socket-exit tail frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/183 -->
