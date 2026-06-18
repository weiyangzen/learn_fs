# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/filesystem_driver.rs

Purpose: small async test driver for invoking filesystem operations against a mounted temporary path.

Important APIs: `FilesystemDriver { mountpoint }`, `new`, and async `mkdir`.

Control flow and state: `mkdir` joins the requested absolute path to the mountpoint, calls blocking `nix::unistd::mkdir` inside `tokio::task::spawn_blocking`, and returns the resulting nix error or success. It converts `Mode` to raw mode bits.

Dependencies and integration: used by `mkdir` tests through `Runner::driver`. Depends on `AbsolutePathBuf`, `nix`, `tokio`, and local `Mode`.

Risks and tests: currently only supports mkdir. Path joining strips the leading slash with `without_root`, so absolute test paths are interpreted under the temp mount.
