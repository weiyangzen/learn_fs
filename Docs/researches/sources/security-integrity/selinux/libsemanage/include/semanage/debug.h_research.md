# sources/security-integrity/selinux/libsemanage/include/semanage/debug.h

Purpose: exposes libsemanage's public message-reporting API. It lets applications inspect the current message context and install a printf-style callback or suppress messages.

Important APIs/types/functions: defines message levels `SEMANAGE_MSG_ERR`, `WARN`, and `INFO`; declares `semanage_msg_get_level`, `get_channel`, `get_fname`, and `semanage_msg_set_callback`. The callback receives caller data, the semanage handle, and a format string.

Control flow: internal code emits messages through debug macros, which populate level/channel/function fields on the handle and invoke the registered callback. The public getters let the callback inspect that state while formatting or routing output.

State and persistence behavior: purely in-memory per-handle state. Installing a callback changes runtime reporting only and has no policy-store side effects.

Dependencies and integration points: used by public applications, SWIG bindings, the internal `debug.h` macros, and the relay handler that forwards libsepol messages into libsemanage callbacks.

Risks: callbacks must be printf-compatible and avoid unsafe reentrant libsemanage operations. Passing NULL suppresses messages, which can hide actionable errors. Test signals include callback invocation level/function metadata, default formatting, suppression behavior, and preservation of `errno` across message emission.
