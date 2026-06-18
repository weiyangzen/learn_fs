# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/xattrs.c

## Purpose
Provides FSAL_PROXY_V4 extended-attribute operation symbols as unsupported stubs.

## Important APIs, Types, and Functions
Implements list, id-by-name, get-by-name, get-by-id, set-by-name, set-by-id, get-xattr-attrs, remove-by-id, and remove-by-name functions.

## Control Flow
Every function immediately returns `fsalstat(ERR_FSAL_NOTSUPP, 0)`.

## State and Persistence Behavior
No state, caching, persistence, or remote calls. Xattr mutation is impossible through these functions.

## Dependencies and Integration Points
Included via `proxyv4_fsal_methods.h`; operation-vector installation depends on surrounding FSAL defaults.

## Risks
Module fsinfo advertises `named_attr = true`, while all xattr operations return not supported, creating a capability mismatch.

## Test Signals
Negative xattr tests should consistently receive `ERR_FSAL_NOTSUPP`.
