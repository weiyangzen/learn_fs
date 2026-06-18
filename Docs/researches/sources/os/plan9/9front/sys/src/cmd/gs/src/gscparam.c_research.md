# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscparam.c

## Role

`gscparam.c` implements Ghostscript’s default C in-memory parameter-list implementation for reading, writing, requesting, enumerating, and forwarding typed device/interpreter parameters.

This is parameter plumbing infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_c_param_list_alloc`
- `gs_c_param_list_write`
- `gs_c_param_list_set_target`
- `gs_c_param_list_write_more`
- `gs_c_param_list_release`
- `gs_c_param_list_read`

The public procedure table methods are installed into `gs_param_list` and used through generic parameter APIs.

## Core Data Model

Each parameter is stored as a linked `gs_c_param` node with:

- key and key ownership flag
- typed value union
- `gs_param_type`
- optional alternate typed data
- next pointer

`gs_param_type_any` marks requested-but-not-written parameters.

## Write Behavior

Writes allocate parameter nodes, copy typed values, and deep-copy non-persistent string/name/array storage. String and name arrays also copy second-level string data when needed.

Collections are represented as nested `gs_c_param_list` instances and stored as dict, int-key dict, or array values.

## Read Behavior

Reads search the local list first, optionally fall back to a target parameter list, and then coerce values to requested types. A special int-array-to-float-array conversion path allocates alternate typed data and caches it in the parameter node.

Enumeration walks the linked list. Error policy defaults to ignore, and commit is a no-op.

## GC Support

Defines composite GC descriptors for parameter nodes and lists. Aggregate parameters recurse into nested lists; other typed values delegate to `gs_param_typed_value` GC helpers.

## Notable Risks

- List insertion is head-first, so enumeration returns reverse write order.
- `alternate_typed_data` lifetime is tied to list release; callers must not retain converted arrays afterward.
- `persistent_keys = true` by default means key strings are usually not copied, so caller key storage must remain valid unless persistence is disabled.
