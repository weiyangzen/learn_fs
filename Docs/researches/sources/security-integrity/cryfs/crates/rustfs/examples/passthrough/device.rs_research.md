# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/device.rs

Purpose: Implements an object-based device that maps filesystem operations onto a real base directory.

Important APIs/types/functions: `PassthroughDevice::new` stores `basedir`; `apply_basedir` joins requested absolute paths. `Device` impl provides rootdir, optimized lookup, rename, and statfs.

Control flow: lookup and rename translate CryFS absolute paths into host paths. `statfs` runs blocking `nix::sys::statfs::statfs` on a blocking thread and converts platform-specific values to `Statfs`.

State and persistence behavior: persistent state is the host filesystem under `basedir`; this object stores only the base path.

Dependencies and integration points: used by the passthrough example main with `ObjectBasedFsAdapterLL`; integrates `tokio::fs`, `nix`, and path wrappers.

Risks: base-path joining must prevent escaping through invalid path components; safety relies on CryFS path types. Platform-specific statfs conversion uses unwraps and a macOS filename-length guess.

Test signals: smoke tests should check root lookup, rename, statfs, and path containment under the base directory.
