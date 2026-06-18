# sources/test-tools/syzkaller/vm/starnix/starnix.go

Purpose: implements the syzkaller VM backend for Fuchsia Starnix, registering `targets.Starnix` with `vmimpl` and exposing Starnix containers as SSH-driven test instances.

Important APIs/types/functions: `Config`, `Pool`, `instance`, `ctor`, `Pool.Create`, `Pool.Close`, `instance.boot`, `startFuchsiaVM`, `startFuchsiaLogs`, `startSshdAndConnect`, `connect`, `ffxCommand`, `runFfx`, `Copy`, `Forward`, `Run`, `Info`, `setFuchsiaVersion`, `getFuchsiaBuildDir`, and `GetToolPath`. The backend implements `vmimpl.Infoer`.

Control flow: `ctor` parses JSON config and creates an isolated temporary `ffx` directory. `Create` resolves `ffx`/`ffx-log` from Fuchsia `tool_paths.json`, copies selected default `ffx` config values into the isolate, discovers SSH keys, records the Fuchsia version, then boots. Boot stops any stale emulator by name, starts a headless emulator, runs Starnix Alpine and sshd components, copies the SSH authorized key into the component namespace, creates a host-local SSH bridge, and starts `ffx log` into an `OutputMerger`. `Run` starts host `ssh`, attaches stdout/stderr streams, and uses `vmimpl.Multiplex`.

State and persistence: runtime state is mostly process handles, pipes, ports, the `ffx` isolate directory, and output merger state. Persistent source-side reads are `.fx-build-dir` and `tool_paths.json`; guest copies go to `/tmp`. `Pool.Close` removes the isolate directory so `ffx` daemon state is discarded.

Dependencies and integration: depends on Fuchsia checkout layout, `ffx`, `ffx-log`, component URLs for `syzkaller_starnix`, host SSH/SCP, syzkaller `osutil`, `config`, `targets`, and `vmimpl` output/SSH helpers. It integrates with the generic `vm` monitor through the `vmimpl.Instance` contract.

Risks: heavily tied to Fuchsia tooling and component monikers; SSH bridge readiness is a fixed sleep; `Forward` allows only one reverse-forward port; `Diagnose` is empty, so crash triage relies on existing logs; `Close` ignores most command errors; `GetToolPath` assumes current Fuchsia build metadata.

Test signals: no direct test file is assigned. Practical coverage comes from VM integration runs that validate emulator boot, Starnix sshd startup, SCP, `Run`, and log merger behavior.
