# File Research: sources/os/plan9/9front/sys/src/9/kw/cga.c

Implements a simple CGA text console backend.

Key elements:
- Writes characters and attributes into CGA memory at `0xB8000`.
- Handles newline, tab, backspace, scrolling, and cursor updates.
- Installs `screenputs` during `screeninit`.
- Uses a lock but avoids deadlock when printing from interrupt context.

Dependencies:
- Uses kernel screen output hook and memory mapping macros.

Research notes:
- Port I/O functions are stubbed with TODO macros, so hardware cursor register access is effectively inactive here.
