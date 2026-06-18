# sources/user-network-fs/libfuse/example/meson.build

## Purpose

`example/meson.build` declares libfuse example executables and their platform-specific inclusion rules. It builds simple C examples, threaded notification examples, Linux service examples, and optional C++ examples without installing them. The source was read as a complete 71-line file.

## Important APIs, Types, and Functions

Important variables are `examples`, `single_file_examples`, and `threaded_examples`. Meson constructs include `configure_file`, `foreach ex : examples`, `foreach ex : single_file_examples`, `foreach ex : threaded_examples`, `add_languages('cpp', ...)`, and `executable(...)`.

## Control Flow

At configure time Meson selects examples based on `platform`: non-BSD adds `passthrough_ll`, `hello_ll_uds`, and `null`; Linux adds socket units and service examples; threaded examples always link `thread_dep`; C++ examples build when the compiler is available and platform is not DragonFly.

## State and Persistence Behavior

No runtime state. It generates socket unit files from templates for Linux-only examples and records build graph policy.

## Dependencies and Integration Points

It integrates `libfuse_dep`, `thread_dep`, and generated `private_cfg` files. It is the build entry for many files researched in this subset.

## Risks and Edge Cases

Platform filters are coarse and can accidentally include examples unsupported by a specific Unix variant. C++ language enablement is optional, so `memfs_ll` coverage depends on toolchain availability. Build lists must be updated when example source files are added or renamed.

## Test Signals

Run Meson configure/build on Linux, BSD-like platforms, and without a C++ compiler; verify expected targets are present/absent and generated socket files exist only where intended.
