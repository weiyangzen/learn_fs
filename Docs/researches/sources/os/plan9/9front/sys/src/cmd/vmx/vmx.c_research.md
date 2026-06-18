# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vmx.c

## Role

`vmx.c` is the main coordinator for 9front's `vmx` virtual machine runner. It opens the Plan 9 `#X` VM device, builds the guest physical memory map, attaches backing segments, loads the kernel, initializes emulated devices, and runs the VM event loop.

## Major Responsibilities

- Opens `#X/clone` and the per-VM `regs`, `map`, and `wait` files.
- Maintains a lazy register cache over the `regs` file through `rget()`, `rpoke()`, `rcflush()`, and typed helpers.
- Creates non-overlapping `Region` records for guest RAM, VGA, reserved BIOS areas, and optional framebuffer regions.
- Maps guest physical regions into a Plan 9 segment, writes the VM memory map to `#X/.../map`, and exposes helpers like `gptr()`, `gpa()`, `gavail()`, and `gend()`.
- Posts guest exceptions with `postexc()`.
- Launches/resumes execution by flushing dirty registers and writing `go` to the control file.
- Runs a three-source event loop: VM exits from `wait`, timer ticks from `sleeperproc`, and deferred main-thread notifications from `sendnotif()`.
- Parses command-line options for RAM size, serial ports, block devices, NICs, framebuffer/VGA mode, 9P service name, shared segment name, debug, and I/O debug masks.
- Initializes CPU ID filtering, PCI, VGA, virtio/IDE devices, optional 9P, optional kernel configuration callback, then enters `runloop()`.

## Key Data And Control Flow

- `mmap` is the global linked list of physical memory `Region` records.
- `segname` and `segrclose` control the host segment backing guest RAM.
- `ctlfd`, `regsfd`, `mapfd`, and `waitfd` are the VM device control surface.
- `waitch`, `sleepch`, and `notifch` serialize VM exits, periodic device clock work, and callback execution into the main loop.
- `getexit` tracks outstanding VM executions so the event loop knows when it can relaunch.

## Notable Limitations And Risk Areas

- `mkregion()` rejects overlap and alignment problems eagerly; callers must build the physical map in correct order.
- The register cache stores pointers into static load buffers for existing register names and direct string pointers for newly poked names; lifetime expectations matter.
- `rcflush(1)` formats dirty registers into a command-line fragment for `go`, while `rcflush(0)` writes newline-separated updates to `regsfd`.
- Timer behavior depends on `nanosec()` and a polling fallback interval; device timers are advanced cooperatively.
- `sendnotif()` runs callbacks immediately on the main thread and otherwise queues them, so callbacks must be safe under the VM event-loop locking model.
