# sources/user-network-fs/libtirpc/tirpc/rpc/des.h

Purpose: `des.h` defines the low-level DES parameter structure and software DES entry point used by legacy secure RPC.

Important APIs, types, and functions: It defines `DES_MAXLEN`, `DES_QUICKLEN`, `enum desdir`, `enum desmode`, `struct desparams`, direct/buffer aliases `des_data` and `des_buf`, and `_des_crypt`.

Control flow: Callers fill key, direction, mode, IV, length, and either inline quick data or buffer pointer before invoking DES implementation or historical ioctl paths.

State and persistence behavior: State is caller-owned inside `struct desparams`; CBC mode updates IV behavior in implementation code.

Dependencies and integration points: It integrates with `des_crypt.h`, AUTH_DES, keyserv, and DES block definitions from `auth.h`. Disabled ioctl constants document historical hardware-driver integration.

Risks: DES is obsolete and weak. Buffer selection through a union requires callers to honor `DES_QUICKLEN`. Hardware ioctl support is disabled, so callers must rely on software. Length and alignment requirements need implementation enforcement.

Test signals: Tests should cover CBC/ECB software calls, quick vs buffer storage, bad length rejection, IV update behavior, and parity/key handling with `des_crypt.h`.
