# File Research: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.c

Generated server-side XDR encoder/decoder support for NLMv4.

Decode coverage:
- Primitive helpers for netobj, share mode/access, uint64/int64, uint32/int32, and NLMv4 stats.
- Compound decoders for holder, testrply, stat, res, testres, lock, lockargs, cancargs, testargs, unlockargs, share, shareargs, shareres, notify, and notifyargs.
- Public service decode entry points fill `rqstp->rq_argp` for void, TEST, LOCK, CANCEL, UNLOCK, TEST_RES, RES, NOTIFYARGS, SHAREARGS, and NOTIFY.

Encode coverage:
- Primitive helpers mirror the decoders.
- Compound encoders for holder, testrply, stat, res, testres, lock, lockargs, cancargs, testargs, unlockargs, share, shareargs, shareres, notify, and notifyargs.
- Public service encode entry points write `rqstp->rq_resp` for void, TESTRES, RES, and SHARERES.

Generated-file notes:
- Produced by `xdrgen` from `Documentation/sunrpc/xdr/nlm4.x`.
- Enforces maximum string lengths for caller and notify names before encoding.
- Uses bool-returning decode/encode helpers instead of errno.
