<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248

## Purpose
This fixture covers suspicious RCU usage detection in IPv6 flow-label socket-option handling. The expected title is `INFO: suspicious RCU usage in ipv6_flowlabel_opt`.

## Important APIs, Types, and Functions
The file uses a `TITLE` header and a raw lockdep RCU warning. Parser paths include Linux info-report matching, RCU suspicious usage regexes, function extraction from lockdep reports, and printk cleanup. Important kernel symbols include `do_ipv6_setsockopt.isra.13`, `ipv6_flowlabel_opt`, `dump_stack`, `lockdep_rcu_suspicious.cold.44`, `ipv6_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The reporter sees `[ INFO: suspicious RCU usage. ]`, the file and line `/linux/net/ipv6/ip6_flowlabel.c:543`, lock context, then a call trace. The Linux matcher must classify the report as informational lockdep/RCU output and use `ipv6_flowlabel_opt` from the stack rather than generic lockdep helper frames.

## State and Persistence Behavior
No state is mutated. The durable test contract is the title and raw log; there are no explicit crash type, panic, corruption, or report-boundary headers.

## Dependencies and Integration Points
The fixture depends on syzkaller's Linux RCU suspicious-use patterns and stack parser. It integrates with `TestParse` through the standard report testdata directory.

## Risks and Edge Cases
`debug_locks = 0` and multiple lock lines can make the report look like general lockdep noise. The parser must not suppress it as harmless RCU chatter or title it after `lockdep_rcu_suspicious`.

## Test Signals
A passing parse returns the exact title `INFO: suspicious RCU usage in ipv6_flowlabel_opt` and selects the subsystem frame from the trace.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/248 -->
