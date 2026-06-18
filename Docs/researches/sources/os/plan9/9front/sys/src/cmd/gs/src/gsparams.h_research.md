# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsparams.h

Declares serialization APIs for `gs_param_list`.

Active interface:
- `gs_param_list_serialize(gs_param_list *, byte *, int)`
- `gs_param_list_unserialize(gs_param_list *, const byte *)`

Disabled future interface:
- Stream-based `gs_param_list_puts`
- Stream-based `gs_param_list_gets`

The header currently selects the buffer serializer implemented in `gsparams.c`, while preserving declarations for the stream design behind `#if 0`.
