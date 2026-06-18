# File Research: sources/os/bsd/dragonflybsd/sys/sys/eventhandler.h

`eventhandler.h` is kernel-only and errors out for normal userland inclusion. It defines dynamic event-handler lists and entries, `eventhandler_tag`, and macro APIs for fast and slow eventhandler declaration, definition, invocation, registration, and deregistration.

Fast lists require a link-time owner via `EVENTHANDLER_FAST_DEFINE`; slow lists are created dynamically and found by name. Handler entries carry priority and an opaque argument.

Kernel prototypes cover `eventhandler_register()`, `eventhandler_deregister()`, and `eventhandler_find_list()`. The file also declares standard shutdown event queues and priority constants.
