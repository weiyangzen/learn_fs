# File Research: sources/os/bsd/freebsd-src/sys/sys/random.h

Read completely: 172 lines.

## Purpose
Defines kernel random-device interfaces, entropy source identifiers, harvest helpers, and the userland `getrandom(2)` API flags/prototype.

## Main Elements
- Supports loadable random implementations through function pointers for `read_random`, `read_random_uio`, and `is_random_seeded`; non-loadable builds declare normal functions.
- Enumerates environmental and hardware/pure entropy sources, with a static assertion limiting source count to a word-sized bitset assumption.
- Defines boot entropy module names.
- Declares harvest source mask and queued/fast/direct harvest backends.
- Provides inline harvest wrappers that check `hc_source_mask` before submitting entropy.
- Provides compile-time feature wrappers for UMA and Ethernet entropy harvesting.
- For userland, includes fortified random declarations when enabled.
- Defines `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE`, and declares `getrandom()`.

## Dependencies And Integration
Integrated with randomdev, entropy harvest queues, hardware RNG drivers, UMA/network entropy hooks, boot entropy modules, `uio`, and userland random APIs.

## Risk Notes
Entropy source numbering is mirrored by descriptive strings elsewhere and constrained to fit a bitmask. Loadable-random kernels rely on proper initialization before function-pointer use.
