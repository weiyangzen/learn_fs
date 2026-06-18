# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthorize.hh

## Purpose

`XrdAccAuthorize.hh` defines the public authorization plugin interface and the operation enum used by XRootD authorization checks. The file was read completely.

## Important APIs, Types, and Functions

`Access_Operation` maps server operations to stable indexes from `AOP_Any` through `AOP_Poll`, with `AOP_LastOp` equal to 16. `XrdAccAuthorize` declares virtual `Access()`, an extended-error overload of `Access()`, `Audit()`, and `Test()`. Function pointer typedefs define plugin factories `XrdAccAuthorizeObject_t`, `XrdAccAuthorizeObject2_t`, and wrapper factory `XrdAccAuthorizeObjAdd_t`.

## Control Flow

Server components call `Access()` with an authenticated `XrdSecEntity`, logical path, and operation. Implementations return a nonzero privilege/permit result or zero deny. For `AOP_Any`, implementations return the privilege mask for later `Test()` calls. Plugin loading obtains an object from an extern C factory or uses the statically linked default.

## State and Persistence Behavior

The interface owns no state. Plugin implementations are typically process-lifetime objects. Extended error strings are caller-owned outputs.

## Dependencies and Integration Points

It depends on `XrdAccPrivs.hh`, `std::string`, `XrdSecEntity`, `XrdOucEnv`, and `XrdSysLogger`. It is a cross-module ABI for authorization plugins, wrapper plugins, and server authorization calls.

## Risks and Edge Cases

The operation enum is positional and comments warn that audit/test tables must remain in one-to-one correspondence. Implementations that omit new enum values can fail or read out of bounds. Factory ABI and version metadata must remain stable for shared plugins.

## Test Signals

ABI tests should load a minimal plugin and wrapper plugin. Behavioral tests should call every operation value, including `AOP_Stage` and `AOP_Poll`, through `Access()` and `Test()`.
