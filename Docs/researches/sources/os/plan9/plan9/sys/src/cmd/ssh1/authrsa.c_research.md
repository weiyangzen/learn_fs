# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authrsa.c

SSH1 client RSA authentication method using factotum.

Key responsibilities:
- Starts factotum RSA client RPC.
- Iterates factotum-provided RSA moduli.
- Sends each public modulus in `SSH_CMSG_AUTH_RSA`.
- On challenge, asks factotum to decrypt, unpads RSA data, appends session id, MD5s it, and sends response.

Important function:
- `authrsafn`.

Data flow:
- Server challenge `mpint` -> factotum decrypt -> `rsaunpad` -> 32-byte right-justified value -> append `sessid` -> MD5 -> `SSH_CMSG_AUTH_RSA_RESPONSE`.

Risks/quirks:
- Continues to next key on several factotum/decode failures.
- Alloc size expression `16+(mpsignif(mod)+7/8)` appears precedence-sensitive and likely intends `(bits+7)/8`.
