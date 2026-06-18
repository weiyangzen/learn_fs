# File Research: sources/local-fs/erofs-utils/lib/base64.c

## Purpose
Small base64 encode/decode utility implementation for `liberofs`.

## Important Functions
- `erofs_base64_encode()`: encodes bytes into the standard `A-Z a-z 0-9 + /` alphabet and appends `=` padding.
- `erofs_base64_decode()`: decodes a base64 string, tolerates trailing padding, and returns decoded length or negative errors.

## Behavior
- Decode returns `-2` for invalid characters.
- Decode returns `-1` for invalid residual bits or invalid padded residual data.
- No NUL terminator is written by encode; caller receives output length.

## Interactions
- Uses `liberofs_base64.h` and EROFS integer/bit helpers.

## Notes
The implementation is self-contained and does not allocate memory.
