# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/errors.rs

Purpose: Provides adapters from `std::io::Result` and `nix::Result` to rustfs `FsResult`.

Important APIs/types/functions: `IoResultExt<T>::map_error` maps IO errors through `FsError::from_io_error`; `NixResultExt<T>::map_error` maps nix errno through `FsError::from_nix_error`.

Control flow: no complex flow; both traits transform the error side of `Result`.

State and persistence behavior: none.

Dependencies and integration points: used throughout passthrough device, dir, file, node, symlink, openfile, and utils modules.

Risks: conversion fidelity depends on `FsError` mappings. Call sites that need context lose the original path unless they wrap errors separately.

Test signals: unit tests should verify representative errno mappings such as ENOENT, EEXIST, EACCES, ENOTDIR, and EISDIR.
