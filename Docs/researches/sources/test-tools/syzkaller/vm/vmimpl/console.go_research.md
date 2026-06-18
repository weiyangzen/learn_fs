# sources/test-tools/syzkaller/vm/vmimpl/console.go

Purpose: non-Windows console helpers for VM implementations, covering direct TTY serial consoles and command-backed remote console streams.

Important APIs/types/functions: `OpenConsole`, `tty.Read`, `tty.Close`, `OpenRemoteKernelLog`, `OpenRemoteConsole`, `OpenAdbConsole`, `OpenConsoleByCmd`, `remoteCon.Read`, and `remoteCon.Close`.

Control flow: `OpenConsole` opens a console device with `O_NOCTTY|O_SYNC`, reads termios using platform constants, configures 115200 8N1 non-canonical mode, and returns a lock-protected `tty`. Remote helpers build SSH/ADB/dmesg commands and call `OpenConsoleByCmd`, which creates a long pipe, starts the command with stdout/stderr to the pipe, and returns a `remoteCon` that kills the process and closes the pipe on `Close`.

State and persistence: runtime state is file descriptors, command processes, and read/close locks. No persistent files are written.

Dependencies and integration: depends on `golang.org/x/sys/unix`, `syscall`, `osutil.LongPipe`, and platform-specific `console_*` constants. VM backends add returned readers to `OutputMerger`.

Risks: direct console setup depends on correct ioctl constants per host arch; `OpenRemoteKernelLog` hardcodes `vsoc-01@`; command close kills processes bluntly; direct TTY read serializes reads and returns EOF after close.

Test signals: no direct assigned test. Merger/backend integration validates readers indirectly.
