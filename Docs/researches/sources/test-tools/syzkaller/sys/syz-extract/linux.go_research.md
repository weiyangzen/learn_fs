# sources/test-tools/syzkaller/sys/syz-extract/linux.go

Purpose: Linux backend for extracting constants from kernel headers and optional generated build outputs.

Important APIs/types/functions: `linux.prepare`, `linux.prepareArch`, and `linux.processFile`.

Control flow: `prepare` optionally runs `make mrproper` when the source tree appears dirty and rejects multi-arch extraction without `-build`. `prepareArch` writes stub headers under `buildDir/syzkaller`, optionally creates/updates a kernel config, enables required config options, and builds `init/main.o`. `processFile` assembles a hermetic kernel include list, appends target C flags and extra include dirs, extracts constants from an ELF object, and rewrites 32-bit `__NR_mmap` to `__NR_mmap2` when required.

State and persistence: writes temporary stub headers and kernel build artifacts in the build directory; central driver deletes temporary build dirs created by `-build`.

Dependencies and integration points: depends on `pkg/build.LinuxMakeArgs`, kernel `make`, scripts/config, target compiler settings, and shared extract code.

Risks: build/config mutations are expensive and sensitive to kernel layout. Stub headers can mask missing kernel headers if incorrectly ordered. The mmap compatibility fix assumes `mmap2` is available on affected 32-bit arches.

Test signals: no direct unit tests; heavily validated through regular constant regeneration and generated executor build.
