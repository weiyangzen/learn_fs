# sources/test-tools/syzkaller/vm/gce/gce.go

## Purpose

`gce.go` implements the Google Compute Engine VM backend. It prepares or reuses GCE images, creates instances with per-instance SSH keys, copies binaries, runs commands with serial console capture, detects preemption, and gathers diagnostics.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`. Public constructors are `ctor` and `Ctor`. Important functions include `initGCE`, `Pool.Count`, `Pool.Create`, `Close`, `Forward`, `Copy`, `Run`, `waitForConsoleConnect`, `hasBeenPreempted`, `Diagnose`, `ssh`, `sshArgs`, `serialPortArgs`, `getSerialPortOutput`, and `uploadImageToGCS`.

## Control Flow

`Ctor` validates config, initializes GCE context with retries, optionally uploads a raw disk image as a tar.gz to GCS and creates a GCE image, then returns a pool. `Create` generates an SSH key, builds instance config, deletes stale instances when appropriate, creates the instance, handles conflict by deleting/recreating, selects SSH credentials, and waits for SSH. `Run` starts a serial-console SSH connection, waits for it to attach, starts the workload SSH command, merges console/stdout/stderr, and uses `vmimpl.Multiplex` with preemption detection.

## State and Persistence Behavior

Pool state includes GCE context, config, optional console command, and an `alreadyCreated` map to avoid repeated cross-zone deletion. Instance state includes instance name/zone, per-instance key path, close channel, console writer, timeout scale, and preempted flag. The backend creates/deletes cloud instances, images, GCS objects during image upload, and local SSH key files.

## Dependencies and Integration Points

It depends on `pkg/gce`, `pkg/gcs`, Google API errors, SSH/SCP helpers, serial-port SSH service, crash diagnosis helpers, and target OS metadata. Cuttlefish reuses this backend with a custom console-read command.

## Risks and Test Signals

Risks include cloud quota/transient failures, stale instance conflicts, serial-port permission failures, missed early crash logs before console connect, preemption misclassification, and destructive image deletion by configured name. Tests are mostly integration-level: create/delete instances, upload images, SSH boot, serial console replay, copy failure under preemption, and diagnostics for Linux/FreeBSD/OpenBSD.
