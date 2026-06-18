# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/428

Purpose: Linux reporter parse fixture for syzkaller. It expects `KCSAN: data-race in e1000_clean_rx_irq`, type `KCSAN-DATARACE`, frame `e1000_clean_rx_irq`, corrupted `N`, panicked `N`. The log covers a KCSAN report in the Intel e1000 receive interrupt path.

Important APIs, types, and functions: this tests single-frame KCSAN title extraction. Key frames include `e1000_clean_rx_irq`, `e1000_clean`, `net_rx_action`, `__do_softirq`, `irq_exit`, and idle tail frames.

Control flow: 23 log lines are parsed. The reporter must select the driver receive-clean function as both title frame and `FRAME` value.

State and persistence behavior: expected frame/type/title are stored in headers; runtime parser state is temporary.

Dependencies, integration points, risks, and test signals: this protects KCSAN grouping for network driver interrupt handling. Risks are selecting generic softirq frames or failing without a second racing stack. Passing tests require exact data-race title and frame.
