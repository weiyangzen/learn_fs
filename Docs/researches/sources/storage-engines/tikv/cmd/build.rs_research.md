# sources/storage-engines/tikv/cmd/build.rs

## Purpose
`cmd/build.rs` is a shared build script for TiKV command binaries. It embeds build time and tries to statically link the C++ standard library for GNU/Clang-like toolchains.

## Important APIs, types, and functions
`main()` prints `cargo:rustc-env=TIKV_BUILD_TIME=<UTC time>`, gets the C compiler from `cc::Build`, and calls `link_cpp()`. `link_cpp()` selects `libstdc++.a` for GNU-like tools, `libc++.a` for Clang-like tools, and skips Windows/unknown tools. `link_sys_lib()` asks the compiler for `--print-file-name <lib>`, validates an absolute path, then emits `cargo:rustc-link-lib=static:-bundle,+whole-archive=<name>` and `cargo:rustc-link-search`.

## Control flow
Cargo runs the build script before compiling the command crate. The script's printed lines become Cargo build instructions and environment variables for Rust code.

## State and persistence behavior
It does not write files, but it injects `TIKV_BUILD_TIME` into compiled binaries and changes linker behavior.

## Dependencies and integration points
It depends on the `cc` crate, workspace `time` crate, the host compiler, and Cargo build-script protocol. `cmd/tikv-ctl/build.rs` includes this file directly.

## Risks and edge cases
`output().unwrap()` can panic if invoking the compiler fails. Static C++ linking is skipped if the path is non-absolute or lookup fails. Link modifiers are specialized to avoid rlib bundle/whole-archive conflicts and may need updates for new Rust/Cargo linker behavior.

## Test signals
Build logs should show `TIKV_BUILD_TIME`, static C++ link directives on GNU/Clang, no C++ static link on Windows, and successful command binary linking.
