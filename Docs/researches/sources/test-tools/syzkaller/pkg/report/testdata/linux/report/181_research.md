<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181

## Purpose
This fixture verifies warning parsing for duplicate proc entry registration in the iptables CLUSTERIP target. The expected title is `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, with `PANICKED: Y`. The console line `proc_dir_entry 'ipt_CLUSTERIP/172.20.0.170' already registered` gives the semantic reason for the warning.

## Important APIs, Types, And Functions
The fixture API is the syzkaller report header plus raw Linux log. Parser components exercised include warning extraction, source-location stripping from `fs/proc/generic.c:330`, function-title selection from `proc_register` and caller context, and panic-on-warn recognition. Important kernel frames include `proc_register`, `proc_create_data`, `clusterip_tg_check`, `xt_check_target`, `find_check_entry`, `translate_table`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `sctp_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The test loader reads the metadata, then the Linux reporter finds the cut-here warning and call trace. The parser should use the CLUSTERIP caller to produce a subsystem-specific title instead of the generic `proc_register` frame. The syscall path flows from `setsockopt` through SCTP/IP netfilter hooks into iptables table translation and target validation.

## State And Persistence
Persistent state is the expected title, type, panic flag, and the 130-line log. Runtime values such as IP address, PID, stack addresses, and register contents are volatile parser input. There is no local mutation beyond the test harness comparing parsed output to this file.

## Dependencies And Integration Points
The fixture depends on Linux warning regexes, proc-registration special-case title cleanup, netfilter stack parsing, and panic detection. It is integrated by `TestParse` via the `report` testdata directory and helps keep Linux reporter behavior stable for CLUSTERIP setup failures.

## Risks
The parser could collapse the warning to `WARNING in proc_register`, omit the CLUSTERIP context, or miss the panic flag because the panic line appears immediately after the warning. Another risk is treating the human-readable proc_dir_entry line as the title instead of the expected normalized title.

## Test Signals
Useful checks are the title `WARNING: proc registration bug in clusterip_tg_check`, type `WARNING`, and `PANICKED: Y`. The selected report should include both the duplicate proc entry line and the call path through `clusterip_tg_check`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/181 -->
