# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egdecrypt.c

Implements `egdecrypt(EGpriv *priv, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The ciphertext is packed as `gamma << shift + delta`, where `shift` is derived from the modulus significant-bit count rounded to a digit boundary. Decryption extracts `gamma` and `delta`, computes `gamma^secret mod p`, inverts that value modulo `p`, multiplies by `delta`, and reduces modulo `p`.

The function allocates `out` if nil, uses temporary `gamma` and `delta`, frees them, and returns the plaintext magnitude in `out`.
