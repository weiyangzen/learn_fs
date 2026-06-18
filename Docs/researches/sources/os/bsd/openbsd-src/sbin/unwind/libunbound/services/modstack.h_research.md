# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/modstack.h

## Role

Declares the module stack abstraction used by the mesh and daemon environment.

## Main Type

- `struct module_stack`: stores `num` modules and an array of borrowed `struct module_func_block*` pointers.

## Public API

- `modstack_init`: set an empty stack.
- `modstack_free`: free the module function-block pointer array and reset state.
- `modstack_call_startup`: configure an empty stack and run module startup hooks.
- `modstack_config`: parse `module_conf` into a module function-block array.
- `module_factory`: map one config token to a module function block and advance the parse pointer.
- `module_list_avail`: list compiled-in module names.
- `modstack_call_init`: initialize modules and validate reload ordering.
- `modstack_call_deinit`: deinitialize modules.
- `modstack_call_destartup`: run module shutdown hooks for modules with startup resources.
- `modstack_find`: locate a module index by name.
- `mod_get_mem`: query a named module's memory usage.

## Research Notes

- The header makes clear that the stack stores references to module function blocks, not owned module instances.
- `MAX_MODULE` and the `module_func_block` contract are supplied by the broader Unbound module framework.
