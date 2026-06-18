# sources/test-tools/syzkaller/pkg/cover/backend/modules.go

Purpose: discovers local kernel and Linux module objects, extracts module names/sizes, and reconciles VM-reported load addresses with local object metadata.

Important APIs/types/functions: `DiscoverModules`, `discoverModulesLinux`, `locateModules`, `getModuleName`, `searchModuleName`, `getKaslrOffset`, and `FixModules`.

Control flow: `DiscoverModules` creates a dummy module for the kernel `.text`, then, for Linux, walks kernel object directories and additional module directories for `.ko` files. Each `.ko` is mapped by module name, keeping first directory priority, and sized from its `.text` section. `getModuleName` prefers `.modinfo` `name=` and falls back to `.gnu.linkonce.this_module`. `FixModules` matches VM modules to local modules by name, subtracts kernel KASLR offset, copies size/path, and drops unknown modules.

State and persistence: all state is in-memory maps/slices. Filesystem walking is read-only.

Dependencies and integration: depends on ELF helpers in `elf.go`, syzkaller `vminfo.KernelModule`, target OS metadata, and logging. It feeds `backend.Make` and callback verification in report generation.

Risks: fallback module-name extraction from `.gnu.linkonce.this_module` returns raw section bytes, potentially including padding. Name fallback in `locateModules` uses `strings.TrimSuffix(filepath.Base(path), "."+filepath.Ext(path))`, which can leave a trailing dot for `.ko` paths. Local/VM mismatches silently drop modules in `FixModules`.

Test signals: `modules_test.go` is manual/skipped unless a module dir flag is provided. Main validation is indirect through report tests and real syz-manager module coverage.
