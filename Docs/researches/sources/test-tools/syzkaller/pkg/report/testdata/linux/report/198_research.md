<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198

## Purpose
This long fixture validates a general protection fault in IPv6 iptables table traversal or setup. Expected title is `general protection fault in ip6t_do_table`, alt `bad-access in ip6t_do_table`, type `DoS`, and `PANICKED: Y`.

## Important APIs, Types, And Functions
The raw 438-line log includes allocation failure, KASAN-enabled GPF text, netfilter allocation/setup frames, and fatal panic. Parser behavior under test includes GPF recognition, title selection from netfilter context, panic detection, and not being distracted by allocation diagnostics. Important frames include `warn_alloc`, `__vmalloc_node_range`, `kvmalloc_node`, `xt_alloc_table_info`, `xt_alloc_entry_offsets`, `translate_table`, `do_ip6t_set_ctl`, `nf_setsockopt`, `ipv6_setsockopt`, and the expected `ip6t_do_table` title signal.

## Control Flow
The Linux reporter scans through allocation warnings into a general protection fault and later panic. The runtime path involves IPv6 netfilter table setup and packet/table logic; the parser is expected to select `ip6t_do_table` as the meaningful crash site despite earlier allocation stack frames and voluminous memory diagnostics.

## State And Persistence
The fixture persists the expected metadata and a large raw console report. Dynamic state includes memory pressure counters, addresses, register dumps, PIDs, and netfilter table data. There is no code state beyond golden test input.

## Dependencies And Integration Points
It depends on Linux GPF matchers, netfilter title heuristics, panic detection, and report-boundary trimming for large logs. It integrates with the report parser's DoS classification path rather than KASAN-specific crash types.

## Risks
The parser could title the report from allocation helper frames such as `xt_alloc_entry_offsets` or from `translate_table`, missing the expected `ip6t_do_table`. Long memory diagnostics can also shift boundaries or hide the fatal panic line.

## Test Signals
Stable checks are exact title, alt, type `DoS`, and panic true. The selected report should retain GPF text and enough netfilter stack context to justify `ip6t_do_table`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/198 -->
