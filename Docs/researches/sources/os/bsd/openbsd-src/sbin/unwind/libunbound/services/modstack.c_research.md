# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.c

## Role

Implements configuration, factory lookup, startup/init/deinit, reload validation, and memory introspection for Unbound's ordered module stack.

## Main Behavior

- `count_modules` counts whitespace-separated module names in `module_conf`.
- `modstack_init` and `modstack_free` initialize/free the dynamic array of `module_func_block*`.
- `modstack_config` validates module count, allocates the function-block array, parses each configured module with `module_factory`, and reports unknown/uncompiled modules.
- `module_list_avail` returns the statically compiled module names in execution order availability: `dns64`, optional `python`, optional `dynlib`, optional `cachedb`, optional `ipsecmod`, optional `subnetcache`, optional `ipset`, then `respip`, `validator`, `iterator`.
- `module_funcs_avail` maps the names to each module's `*_get_funcblock` provider.
- `module_factory` skips leading whitespace, matches a configured token by prefix against available module names, advances the caller's string pointer, and returns the function block.

## Lifecycle

- `modstack_call_startup` requires an empty stack, configures it, then calls optional module `startup` hooks.
- `modstack_call_init` verifies reload ordering against `module_conf`, rejects reordered modules that have startup/destartup hooks, rebuilds the stack if only restartable modules changed, clears `env->need_to_validate`, and calls each module `init`.
- `modstack_call_deinit` calls every module `deinit`.
- `modstack_call_destartup` calls optional module `destartup`.

## Utility

- `modstack_find` returns a module index by exact name.
- `mod_get_mem` finds a module by name in the active mesh stack and calls its `get_mem` hook.

## Research Notes

- Function pointer calls are guarded through `fptr_wlist` checks before invocation.
- Module matching uses `strncmp` with module-name length after skipping whitespace; the surrounding parsing assumes whitespace-separated config tokens.
- Reload behavior explicitly distinguishes modules that require startup/destartup from modules that can be reconfigured by rebuilding the stack.
