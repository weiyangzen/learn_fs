# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/13` is a NetBSD report fixture for a UBSan panic titled `UBSan: Undefined Behavior in route_output`. The panic describes a member access through a misaligned address for `struct rt_msghdr` in `sys/net/rtsock_shared.c:667:41`, and the stack points to `route_output()` after the UBSan type-mismatch handler.

The fixture verifies that the NetBSD reporter can distinguish full UBSan panic reports from simpler boot-time UBSan lines, skip the UBSan handler frames, and derive the crash title from the kernel function that triggered the undefined behavior.

## Important APIs, Types, And Functions

Parser-side APIs and functions involved are:

- `netbsdOopses` in `pkg/report/netbsd.go`, specifically the `UBSan: Undefined Behavior` format inside the `panic: ` oops group.
- The fallback `UBSan:` oops format, which is used by shorter UBSan messages but should not override this richer panic pattern.
- `bsd.Parse` and `simpleLineParser`, which extract the report from the full console transcript.
- `bsd.Symbolize` and `bsd.symbolizeLine`, which handle NetBSD frame lines such as `route_output() at netbsd:route_output+0x1676`.

The crash-log functions are the UBSan runtime path `HandleTypeMismatch.part.1` and `HandleTypeMismatch`, followed by networking and socket functions: `route_output`, `raw_send`, `route_send_wrapper`, `sosend`, `soo_write`, `do_filewritev.part.1`, `sys_writev`, `sys___syscall`, and `syscall`. The central data type named by the panic is `struct rt_msghdr`, whose alignment requirement is the source of the UBSan report.

## Control Flow

The represented runtime flow is a user-space syzkaller executor writing routing-socket data through `writev`. The call path moves from the syscall layer to socket output and then into routing message handling:

1. `sys___syscall`/`sys_writev` receive the write request.
2. `soo_write` and `sosend` send data through the socket layer.
3. `route_send_wrapper` and `raw_send` dispatch the raw route socket message.
4. `route_output` accesses a misaligned `struct rt_msghdr`.
5. UBSan's type-mismatch handler reports undefined behavior and panics.
6. NetBSD enters DDB, prints the stack, registers, process table, locks, pages, and related diagnostic state.

For syzkaller parsing, the decisive line is the panic line with `UBSan: Undefined Behavior`, followed by the stack segment where `route_output()` appears after `HandleTypeMismatch`. The long DDB suffix is a stress case for report bounds and duplicate-crash avoidance.

## State And Persistence Behavior

The fixture is immutable repository testdata. The captured runtime state includes:

- LWP `851.285` in `syz-executor.4`, stopped at `breakpoint+0x5`;
- the routing-socket send path's active socket lock initialized at `soinit`;
- system process listings with multiple syzkaller executor and fuzzer threads;
- locks wanted by kernel helper threads and a CPU-held spin lock;
- page-state tables emitted by `show all pages`.

No persistent application data is read or written by the fixture. Its persistence role is regression coverage for parser behavior across future syzkaller and NetBSD changes.

## Dependencies

The fixture depends on NetBSD KUBSAN diagnostic formatting. Important textual dependencies include:

- `panic: UBSan: Undefined Behavior in <file>:<line>:<col>, ...`;
- UBSan handler frames named `HandleTypeMismatch`;
- NetBSD routing stack frames with `netbsd:` offsets;
- syscall number and DDB register/table formatting.

The report parser depends on regular expressions that assume the UBSan panic includes at least one handler frame and then a subsequent function frame that can be captured as the crash site. The symbolizer depends on kernel object symbols if source-line expansion is requested.

## Integration Points

This numbered fixture is automatically included by `forEachFile` for the NetBSD target. It complements report `14`, which is a short fallback UBSan message without a full panic/stack. Together they exercise both the rich `panic: UBSan: Undefined Behavior` path and the generic `UBSan:` path in `netbsdOopses`.

The kernel-domain integration point represented by the log is NetBSD route-socket output. From the parser's perspective, the important integration is that the extracted title should name `route_output`, not the UBSan handler, syscall wrapper, or raw socket send wrapper.

## Risks

The highest risk is title misclassification. If the parser captures `HandleTypeMismatch` instead of `route_output`, syzkaller would bucket the crash under the sanitizer runtime rather than the faulty routing code. If the generic `UBSan:` fallback fires before the richer panic format, the title could degrade to `UBSan: Undefined behavior`.

The file also carries truncation and noise risks because the DDB tail contains many addresses and function-like strings. Parser changes must keep report extraction bounded enough for performance and stable deduplication, while retaining the initial stack that identifies the fault.

## Test Signals

The expected signal is `UBSan: Undefined Behavior in route_output`. Passing tests demonstrate that `Reporter.Parse` recognizes the crash, selects the richer UBSan panic format, and extracts `route_output` as the functional crash site. Symbolization coverage is present through `netbsd:<function>+0x<offset>` stack lines in the extracted report.
