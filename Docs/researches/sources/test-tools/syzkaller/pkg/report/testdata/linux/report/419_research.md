# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/419

Purpose: Linux reporter parse fixture for syzkaller. It expects `INFO: task hung in ld_usb_write`, alternate `hang in ld_usb_write`, type `HANG`, corrupted `N`, panicked `Y`. The body is a hung task in USB control-message write for the LD USB driver.

Important APIs, types, and functions: this tests hung-task parsing and stack filtering. Key frames include `schedule`, `wait_for_completion_timeout`, `usb_start_wait_urb`, `usb_control_msg`, `ld_usb_write`, `__vfs_write`, `vfs_write`, and syscall write frames.

Control flow: 115 log lines contain the blocked task and lock debug data. The parser must skip scheduler/wait helpers and select the device write operation; panic is set because the hung task triggers panic in this fixture.

State and persistence behavior: fixture headers persist expected parser output; runtime state is transient crash matching and flag extraction.

Dependencies, integration points, risks, and test signals: this protects hang classification for USB write paths. Risks are selecting `wait_for_completion_timeout` or generic VFS/syscall frames. Passing tests require HANG type, panic `Y`, title/alternate equality, and non-corruption.
