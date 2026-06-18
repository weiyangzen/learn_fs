# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsagen.c

Implements `dsagen(DSApub *opub)`, generating a DSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

If an existing public parameter set is supplied, it copies `p` and `q`; otherwise it allocates them and calls `DSAprimes`. It then computes a generator `alpha` by selecting random `g`, reducing it modulo `p`, and exponentiating by `(p-1)/q` until the result is not one.

The secret is generated randomly, reduced modulo `p`, and the public key is `alpha^secret mod p`. Temporary `mpint`s are freed before return, and the resulting `DSApriv` owns copied/generated parameters, `alpha`, public key, and secret.
