# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddstack.h

Minimal dictionary-stack API subset needed by dictionary code.

Declares:
- `dstack_set_top`: refresh cached top dictionary data after stack/dictionary changes.
- `dstack_dict_is_permanent`: checks whether a dictionary is one of the permanent stack dictionaries.

This header breaks a coupling loop between dictionary implementation and dictionary stack internals.
