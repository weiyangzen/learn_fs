# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iddstack.h

Declares the minimal dictionary-stack API needed by dictionary code.

Key points:
- Forward-declares `dict_stack_t`.
- Declares `dstack_set_top`, which refreshes cached top-dictionary lookup values.
- Declares `dstack_dict_is_permanent`, which tests whether a dictionary is one of the permanent stack dictionaries.

Research notes:
- This breaks a dependency cycle between dictionary implementation and dictionary-stack implementation.
