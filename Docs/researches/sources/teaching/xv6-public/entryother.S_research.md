# File Research: sources/teaching/xv6-public/entryother.S

Startup assembly copied to low memory for non-bootstrap CPUs.

Key behavior:
- Starts APs in 16-bit real mode, clears segment registers, installs a bootstrap GDT, and enters 32-bit protected mode.
- Enables paging using a page directory pointer written by `startothers`.
- Loads the AP stack pointer from `start-4` and calls the entry function pointer from `start-8`.
- Reads the bootstrap page directory physical address from `start-12`.
- Falls into Bochs breakpoint/spin path if the AP entry call returns.

Important interactions:
- `main.c:startothers` copies this binary to `0x7000` and patches stack/function/page-table words just before it.
