# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsSecurity.hh

## Purpose

This header defines authorization helper macros used by OFS methods. It centralizes access checks, error reporting, and security identity propagation into opaque environments.

## Important APIs, types, and functions

`AUTHORIZE(usr, env, optype, action, pathp, edata)` checks `XrdOfsFS->Authorization` when a user is present, calls `Access()`, and on failure reports `EACCES` through `XrdOfsFS->Emsg()` before returning `SFS_ERROR` from the enclosing function. `AUTHORIZE2()` applies two authorization checks. `OOIDENTENV()` copies `SEC_USER` and `SEC_HOST` into an `XrdOucEnv`.

## Control flow

Call sites invoke these macros before sensitive filesystem operations. Failure short-circuits the caller, so the macros are not expression helpers; they assume local variables such as `epname` and compatible return types.

## State and persistence behavior

The macros do not own state. They read the global `XrdOfsFS` and its authorization plugin, and mutate an environment object in `OOIDENTENV()`.

## Dependencies and integration points

The header includes `XrdAccAuthorize.hh` and expects OFS globals, SFS return codes, errno values, and `XrdSecEntity`/`XrdOucEnv` style objects at call sites. It integrates with most user-facing OFS operations.

## Risks and test signals

Macro control flow can hide returns and variable dependencies. Tests should cover operations with no user, no authorization plugin, allowed access, denied access with extra text, and environment identity propagation. Refactors should be careful not to call `AUTHORIZE()` inside functions with incompatible return types or missing `epname`.
