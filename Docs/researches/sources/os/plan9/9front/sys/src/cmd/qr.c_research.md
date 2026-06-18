# File Research: sources/os/plan9/9front/sys/src/cmd/qr.c

This file implements a standalone QR-code encoder that reads input from stdin and writes a Plan 9 image-like bitmap stream.

Key responsibilities:
- Supports QR numeric, alphanumeric, and byte modes.
- Supports error correction levels L, M, Q, and H.
- Selects a QR version automatically or uses `-v`.
- Encodes payload bits, pads codewords, computes Reed-Solomon error correction, interleaves blocks, builds base QR patterns, fills data modules, evaluates masks, writes format/version bits, and finalizes module values.
- `main()` reads up to 8192 bytes, calls `qrcode()`, and writes a `k8` image header followed by raw module bytes.

Important functions:
- `qrinit()` initializes polynomial and block-capacity tables from embedded data.
- `formsel()` chooses version/level capacity.
- `encode()` serializes the chosen QR payload mode.
- `ecc()` computes Reed-Solomon parity over GF(256).
- `codewords()` interleaves data and ECC codewords according to QR block layout.
- `basepat()`, `fill()`, `mask()`, `evaluate()`, `format()`, and `version()` construct and score the QR matrix.

Implementation notes:
- Static tables include GF exponent/log tables, alignment positions, generator polynomials, and all version/level block layouts.
- Alphanumeric mode accepts both uppercase and lowercase letters by mapping them to the same table values.
