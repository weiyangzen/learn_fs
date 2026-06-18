# File Research: sources/os/bsd/dragonflybsd/sys/sys/random.h

Randomness device/getrandom flags and kernel entropy API declarations.

Key responsibilities:
- Defines legacy `/dev/random` memory interrupt ioctls.
- Defines `getrandom()` flags: `GRND_RANDOM`, `GRND_NONBLOCK`, and `GRND_INSECURE`.
- Defines kernel entropy source IDs and per-CPU source flag.
- Defines `struct random_softc` for interrupt-source tracking.
- Declares kernel RNG initialization, entropy input, random read, and kqueue filter APIs.
- Declares userland `getrandom()`.

Important behavior:
- Kernel entropy sources distinguish seeding, timing, interrupts, CPU RNGs, crypto hardware, virtio, threads, and TPM.
- `read_random()` takes an `unlimited` flag.
- `add_buffer_randomness_src()` accepts explicit source IDs.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Kernel section uses `struct knote`.

Notable risks:
- Source ID space is fixed by constants; new sources must avoid collisions.
- `GRND_INSECURE` is visible API and must be handled intentionally by implementation.
