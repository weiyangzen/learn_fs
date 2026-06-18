# sources/user-network-fs/samba/source3/libnet/libnet_join.h

## Purpose

Declares the source3 libnet join/unjoin public interface.

## Important APIs, Types, and Functions

Forward-declares `struct messaging_context` and declares `libnet_join_ok`, `libnet_init_JoinCtx`, `libnet_init_UnjoinCtx`, `libnet_Join`, and `libnet_Unjoin`. The concrete join/unjoin context structures are generated in `ndr_libnet_join.h` and used by callers plus the implementation.

## Control Flow

Callers allocate a join or unjoin context, fill inputs and credentials, call the operation, and inspect `out.result` plus error strings. `libnet_join_ok` can verify an existing secure channel independently.

## State and Persistence Behavior

The header owns no state. Its functions can mutate remote domain state, local secrets, local config, keytabs, and cached DC hints depending on flags.

## Dependencies and Integration Points

Provides the stable include surface for command-line tools and other source3 code that need join functionality.

## Risks and Test Signals

Risks center on API misuse: contexts must be initialized and populated correctly. Tests should compile consumers against this header and exercise success/failure through initialized contexts.
