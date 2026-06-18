# sources/test-tools/syzkaller/vm/virtualbox/virtualbox.go

Purpose: implements a VirtualBox-backed syzkaller VM pool that clones a named base VM, configures SSH NAT and a serial console, runs commands over SSH, and streams kernel output through the common VM monitor.

Important APIs/types/functions: `Config` (`base_vm_name`, `count`), `Pool`, `instance`, `ctor`, `Pool.Create`, `clone`, `boot`, `Forward`, `Close`, `Copy`, `Run`, and `Diagnose`.

Control flow: `ctor` parses config, validates count, base VM name, and `VBoxManage` availability. `Create` assigns a deterministic `syzkaller_vm_<index>` clone name, creates long pipes, calls `clone` and `boot`. `clone` runs `VBoxManage clonevm`, creates a random host NAT forwarding rule to guest port 22, and configures UART1 as a Unix socket. `boot` starts the VM headless, connects to the serial socket, starts an output merger, collects boot output while `WaitForSSH` probes the forwarded SSH port, and returns `BootError` with captured logs on failure. `Run` opens SSH stdout/stderr pipes, optionally adds reverse forwarding, and delegates lifecycle to `vmimpl.Multiplex`.

State and persistence: each instance creates a registered VirtualBox clone plus a serial socket under the workdir. `Close` powers off and unregisters/deletes the clone, closes pipes/sockets, and waits for merger goroutines. Guest copies land at `/`.

Dependencies and integration: depends on `VBoxManage`, host SSH/SCP, Unix domain sockets, syzkaller `osutil`, `vmimpl.SSHOptions`, `WaitForSSH`, `SCP`, and `Multiplex`.

Risks: clone names collide across concurrent pools with the same index; serial socket connection may race VM boot; cleanup ignores `VBoxManage` failures; NAT rule names derive from random ports but are not retried after modify failures; `Diagnose` is a stub.

Test signals: no direct unit tests are assigned. Validation is integration-level: clone, boot, SSH, serial console, command execution, and cleanup must all work on a host with VirtualBox.
