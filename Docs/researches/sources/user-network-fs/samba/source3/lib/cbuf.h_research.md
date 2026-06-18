# sources/user-network-fs/samba/source3/lib/cbuf.h

Purpose: declares the cbuf growable talloc character buffer interface.

Important APIs/types/functions: opaque `struct cbuf` typedef and functions for lifecycle, buffer swapping/takeover, resizing/reserving, writing characters/strings/dwords/printf output, position management, and quoted string emission.

Control flow: callers allocate a `cbuf`, append bytes or formatted text, bookmark positions with `cbuf_getpos()`, rewind with `cbuf_setpos()`, and retrieve NUL-terminated content from any previous position with `cbuf_gets()`.

State and persistence: public API exposes no fields; all state is heap memory attached to the provided talloc context. No durable persistence.

Dependencies/integration: requires Samba's `PRINTF_ATTRIBUTE`, integer types, and talloc conventions supplied by surrounding includes.

Risks/test signals: `cbuf_delete()` is documented as preferred over direct `talloc_free()` despite parent-free working; callers must treat returned pointers as invalid after resize/swap. Tests should compile all prototypes, verify sentinel length behavior, and assert that position invariants hold after clear, setpos, reserve, and takeover.
