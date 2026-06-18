# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/auth.h

Drawterm copy of Plan 9 libauth caller-facing interface.

Key contents:
- Defines `AuthRpc`, `AuthInfo`, `Chalstate`, CHAP/MSCHAP replies, `UserPasswd`, and auth RPC result codes.
- Defines attribute list parsing/matching structures and helper declarations.
- Declares namespace/login/authentication helper APIs, factotum proxy functions, challenge/response functions, user/password retrieval, WEP helper, and RPC lifecycle functions.

Role in this group:
- Provides authentication API contracts used by drawterm’s CPU/authentication paths while building outside Plan 9.

Notable risks:
- This is a header-only contract; security behavior depends on matching implementations elsewhere in drawterm.
- Includes legacy protocol surfaces such as CHAP/MSCHAP and WEP.
