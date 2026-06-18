# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/main.c

`realemu/main.c` implements a 9P service exposing emulated real-mode execution as `realmode` and memory as `realmodemem`, usually mounted before `/dev`. Writes of a `Ureg` to `realmode` execute the emulator and update the register image; reads return the last image. `realmodemem` reads/writes the emulator’s 1 MiB memory buffer.

It initializes memory buses for RAM, ROM, VGA framebuffer passthrough, and bad regions; port I/O buses for PIC, PIT, keyboard, RTC, DMA page registers, A20, PCI config space, and fallback Plan 9 port files `#P/iob`, `#P/iow`, `#P/iol`. Real hardware memory is accessed via `#P/realmodemem`.

`realmode` translates Plan 9 `Ureg` fields into emulator registers, optionally invokes an interrupt vector, runs instruction batches through `xec`, handles traps/pseudo-traps, then writes registers back. `-t` enables CPU trace, `-p` port trace, `-D` 9P chatty mode, `-s` service file, and `-m` mountpoint.

The service serializes execution through a worker proc and channels, supports flush interruption, and rejects concurrent requests with `device is busy`.
