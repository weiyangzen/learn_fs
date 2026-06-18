# sources/test-tools/syzkaller/sys/syz-extract/fuchsia.go

Purpose: Fuchsia backend for extracting constants from Zircon/Fuchsia build outputs.

Important APIs/types/functions: `fuchsia.prepare`, `fuchsia.prepareArch`, `fuchsia.processFile`.

Control flow: prepare hooks are no-ops. `processFile` points clang at Fuchsia prebuilt toolchain, generated Zircon sysroot headers, generated FIDL libraries from `layout.AllFidlLibraries`, and syzlang-requested include dirs, then runs shared extraction with `DefineGlibcUse`.

State and persistence: none beyond temporary compile artifacts.

Dependencies and integration points: depends on a populated Fuchsia checkout/build output layout and `sys/fuchsia/layout` for FIDL include discovery.

Risks: tightly coupled to Fuchsia output directory names and generated include paths. Fuchsia has many broken/missing constants, and sysgen intentionally skips full const-defined checking for this OS.

Test signals: no direct tests here; extraction plus Fuchsia generated package build is the main signal.
