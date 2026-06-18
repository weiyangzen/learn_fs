# sources/test-tools/stress-ng/stress-module.c

Purpose: implements the privileged `module` OS stressor. It repeatedly loads a kernel module with `finit_module()` and optionally unloads it with `delete_module()`, stressing kernel module loading paths and module metadata validation flags.

Important APIs/types/functions: `stress_module_supported()` requires `CAP_SYS_MODULE`. `get_modpath_name()` parses `/lib/modules/$(uname -r)/modules.dep` for either a user-selected `module-name` or default kernel self-test modules. `stress_module_open()` opens `.ko` files directly or decompresses `.ko.xz` through liblzma into an unlinked temp file. `stress_module()` handles options `module-no-unload`, `module-no-modver`, and `module-no-vermag`, validates the module fd with `fstat()`, and loops on `shim_finit_module()`.

Control flow: the stressor creates a temp directory, resolves module path/type, opens or decompresses the module, validates that it is a regular file, optionally removes any preloaded instance, synchronizes, then repeatedly calls `finit_module()` with requested kernel flags and unloads after successful loads unless disabled. Cleanup closes the module fd and removes the temp directory.

State and persistence: this mutates kernel module state. With default behavior it unloads after each successful load and attempts an initial unload; with `module-no-unload`, loaded module state may persist intentionally. Temporary decompression files are unlinked.

Dependencies and integration: Linux-only; depends on `linux/module.h`, `uname`, `modules.dep`, optional liblzma, capability helpers, core module syscall shims, temp-file helpers, and stress-ng synchronization.

Risks and test signals: requires powerful privileges and can affect the host kernel. Dependency modules are not resolved like `modprobe`, compressed formats other than `.xz` are skipped, and `module-no-unload` can leave state behind. Signals are capability skip, module path discovery, successful load bogo increments, and clean unload/close behavior.
