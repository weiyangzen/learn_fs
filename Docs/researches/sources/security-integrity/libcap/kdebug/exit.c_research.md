## sources/security-integrity/libcap/kdebug/exit.c

Purpose: guest-side QEMU exit helper that shuts down or signals status through ISA debug ports.

Important APIs/functions: `clean_exit()` calls `ioperm` and `outw` on ACPI shutdown port `0x604`; `main()` parses optional status, sleeps, uses `outb` on debug exit port `0x501`, and exits 1 if QEMU does not terminate.

Control flow: with wrong argc it attempts clean shutdown; with a status argument it prints status, sleeps three seconds, uses clean shutdown for status 0, otherwise writes `status-1` to the debug-exit port.

State/persistence: performs privileged port I/O in the guest; no files.

Dependencies/integration: Linux `sys/io.h`, x86/QEMU port behavior, QEMU `-device isa-debug-exit`.

Risks: architecture/QEMU-specific; requires I/O permission; status mapping follows QEMU debug-exit convention and can be confusing.

Test signals: run inside the kdebug initramfs and confirm QEMU exits with expected host status for pass/fail.
