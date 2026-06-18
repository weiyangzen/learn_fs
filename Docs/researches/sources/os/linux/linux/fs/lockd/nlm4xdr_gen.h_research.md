# File Research: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.h

Purpose: Generated declarations for NLMv4 service-side XDR encode/decode helpers.

Key contents:
- Includes XDR stream, xdrgen builtins, and generated NLMv4 type definitions.
- Declares decode wrappers for void, testargs, lockargs, cancelargs, unlockargs, testres, res, notifyargs, shareargs, and notify.
- Declares encode wrappers for void, testres, res, and shareres.

Dependencies and integration:
- Included by `nlm4xdr_gen.c` and NLMv4 service code.
- Generated from `Documentation/sunrpc/xdr/nlm4.x`.

Risk notes:
- Must match the generated source and XDR type definitions exactly.
