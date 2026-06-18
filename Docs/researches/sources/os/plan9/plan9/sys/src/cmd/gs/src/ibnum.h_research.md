# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ibnum.h

Defines encoded number constants and decoder prototypes. It documents an Adobe interpreter compatibility bug around byte-swapping native IEEE reals and enables emulation with `BYTE_SWAP_IEEE_NATIVE_REALS`.

Important constants:
- `bt_num_array_value`
- `num_int32`, `num_int16`, `num_float`, `num_float_native`
- `num_msb`, `num_lsb`, `num_array`
- `enc_num_bytes_values` and `encoded_number_bytes`

Exports array-format helpers and primitive number decoders.
