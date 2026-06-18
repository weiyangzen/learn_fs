## sources/test-tools/fio/cconv.c

Purpose: serializes and deserializes `struct thread_options` across fio's client/server protocol using `struct thread_options_pack` and little-endian wire encoding. It exists because thread options contain host pointers, strings, floats, arrays, and variable-length verify/buffer patterns that cannot be sent as a raw structure.

Important APIs and flow: `thread_options_pack_size()` computes the packed size including pattern tails. `convert_thread_options_to_net()` copies scalar fields, string fields, directional arrays, bssplit/zone_split arrays, FDP fields, floating-point union values, and pattern bytes into the packed form. `convert_thread_options_to_cpu()` reverses that mapping, allocating strings and split arrays and validating pattern byte counts against `MAX_PATTERN_SIZE` and the received `top_sz`. `fio_test_cconv()` performs a round-trip pack/unpack/pack comparison with representative verify and buffer patterns.

State and persistence: no persistent storage is used, but CPU conversion allocates heap-owned strings and arrays in `thread_options`; `free_thread_options_to_cpu()` releases those allocations for the conversion test path. The packed object embeds variable data after the fixed structure through `top->patterns`.

Dependencies and integration: depends on `thread_options.h`, endian helpers, `log_err()`, and fio floating-point conversion helpers. It integrates directly with `client.c` when sending `FIO_NET_CMD_UPDATE_JOB` and with server-side job loading/update paths.

Risks and test signals: this is a manually maintained field map, so new `thread_options` fields can silently fail to travel over the network unless both conversion directions and tests are updated. Allocation failures for split arrays are not deeply checked. The strongest local signal is `fio_test_cconv()`, but its own comment says coverage is incomplete.
