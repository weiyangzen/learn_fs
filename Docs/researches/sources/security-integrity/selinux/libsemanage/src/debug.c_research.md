# sources/security-integrity/selinux/libsemanage/src/debug.c

Purpose: implements public and internal message handlers for libsemanage diagnostics.

Important APIs/types/functions: exports `semanage_msg_get_level`, `get_channel`, `get_fname`, `semanage_msg_default_handler`, and `semanage_msg_relay_handler`.

Control flow: getters read the message metadata currently stored on the semanage handle. The default handler formats messages to stderr with level/channel/function context. The relay handler receives libsepol messages and forwards them through semanage's callback mechanism.

State and persistence behavior: only transient per-handle message metadata is read or written. The implementation preserves `errno` through macro emission in internal headers.

Dependencies and integration points: works with public `semanage/debug.h`, internal `debug.h`, libsepol debug callbacks, and any application-installed callback.

Risks: formatting code runs during error paths and must avoid clobbering diagnostics. Test signals include default output for each level, relay from sepolh, NULL callback suppression, and getter values inside callbacks.
