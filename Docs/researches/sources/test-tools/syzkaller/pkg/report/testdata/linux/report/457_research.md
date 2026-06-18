# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/457

Purpose: golden fixture for UBSAN out-of-bounds parsing in the 6pack hamradio line discipline. Expected title is `UBSAN: undefined-behaviour in decode_data` and type is `UBSAN`.

Important APIs, types, and functions: parser behavior includes UBSAN helper filtering and workqueue-context handling. Kernel frames include `decode_data`, `sixpack_receive_buf`, `tty_ldisc_receive_buf`, `tty_port_default_receive_buf`, `flush_to_ldisc`, `process_one_work`, and workqueue thread helpers.

Control flow: the workqueue `events_unbound flush_to_ldisc` processes TTY input, reaches `sixpack_receive_buf`, and UBSAN reports an out-of-bounds condition at `drivers/net/hamradio/6pack.c:843:16`. The title should use `decode_data`.

State and persistence behavior: static fixture with no panic. It persists a TTY workqueue stack rather than a direct syscall-triggered report.

Dependencies and integration points: depends on UBSAN report matching, workqueue context parsing, and network/TTY frame normalization. Integrates hamradio 6pack receive parsing into the regression suite.

Risks: parser frame filtering might select `sixpack_receive_buf` if it misses the more precise `decode_data` frame. Workqueue context should not obscure the report body.

Test signals: `Workqueue: events_unbound flush_to_ldisc`, source location `drivers/net/hamradio/6pack.c:843:16`, `decode_data+0x308/0x3a0`, and TTY ldisc receive frames.
