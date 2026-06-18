# File Research: sources/teaching/os161/kern/include/thread.h

Defines the public thread structure and scheduler lifecycle API. `struct thread` stores a fixed-size name, wait-channel name, state, machine-dependent state, intrusive list node, kernel stack, saved context, CPU pointer, process pointer, optional Hangman actor, and interrupt state fields.

Thread states are `S_RUN`, `S_READY`, `S_SLEEP`, and `S_ZOMBIE`. Stack constants define 4 KiB kernel stacks and helpers for stack-base comparison. The header also declares an array type for threads.

Exports system startup/shutdown functions, CPU startup, panic stop, `thread_fork`, `thread_exit`, `thread_yield`, timer scheduling hooks, migration consideration, and thread-count waiting. Public extension points are intentionally minimal.
