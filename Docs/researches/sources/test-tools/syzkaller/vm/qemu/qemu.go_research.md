# sources/test-tools/syzkaller/vm/qemu/qemu.go

## Purpose

`qemu.go` implements syzkaller's QEMU VM backend. It builds architecture-specific QEMU command lines, boots images or injected kernels, waits for SSH, copies and runs binaries, forwards manager ports, gathers diagnostics, and supports optional snapshot acceleration hooks.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, `instance`, and `archConfig`; `archConfigs` maps OS/arch pairs to defaults. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `Pool.ctor`, `Close`, `boot`, `buildQemuArgs`, `handleVfioPciArg`, `splitArgs`, `Forward`, `targetDir`, `Copy`, `Run`, `Info`, `Diagnose`, `needsRegisterInfo`, `ssh`, and `sshArgs`. The file also contains the 9p `initScript`.

## Control Flow

`ctor` validates config, image/kernel requirements, CPU/memory limits, QEMU binary presence, and captures QEMU version. `Create` prepares special 9p SSH/init files when needed, then retries `Pool.ctor` on transient host-forwarding conflicts. `boot` creates a monitor port, builds args, starts QEMU, starts console merging, optionally performs snapshot handshake, and waits for SSH. `Run` either runs `syz-execprog` on host for host-fuzzer targets or starts an SSH command in the guest target directory and multiplexes output.

## State and Persistence Behavior

Instance state includes QEMU args, image path, workdir, SSH options, monitor connection, pipes, process, output merger, copied host-fuzzer file map, forward port, and optional snapshot state. The backend starts/kills QEMU processes, may write 9p init/key files, copies binaries by SCP, and uses QEMU `-snapshot` to avoid modifying disk images when configured.

## Dependencies and Integration Points

It depends on QEMU system binaries, SSH/SCP, syzkaller target metadata, `vmimpl` multiplex and diagnostics, QMP/HMP helpers in `qmp.go`, and snapshot helpers in platform-specific files. It is the broadest default VM backend used by syz-manager.

## Risks and Test Signals

Command-line construction is complex and architecture-sensitive. Simple whitespace splitting for `QemuArgs` cannot preserve quoted arguments. Port allocation is race-prone but retried for known errors. Diagnosis uses QMP register collection only for selected crash types. Integration signals include boot across all supported OS/arch configs, 9p boot, host-fuzzer mode, VFIO placeholder expansion, forwarding conflicts, copy/run timeout behavior, and register diagnostics.
