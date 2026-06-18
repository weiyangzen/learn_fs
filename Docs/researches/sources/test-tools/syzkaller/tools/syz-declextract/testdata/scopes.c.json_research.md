# sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c.json

Purpose: this golden JSON captures expected extraction for scope/range handling in `scopes.c`.

Important structure: top-level keys are `functions`, `consts`, `structs`, `syscalls`, and `ioctls`. Functions include `__do_sys_scopes0`, fs helpers, and `scopes_helper`. Constants include `FOO_IOCTL*` values relevant to the fixture. Structs include `foo_ioctl_arg` size 8 align 4.

Control-flow and facts: `__do_sys_scopes0` has an arg-independent scope for `aux` flowing to `__fget_light` and `tmp` flowing to return, separate command scopes for `FOO_IOCTL1`, `FOO_IOCTL2/3`, expanded `FOO_IOCTL4` range, `FOO_IOCTL7/8` helper flow, numeric range `100..102`, and default assignment. Helper scopes cover fd allocation, fd lookup, and large constants.

State and persistence: static test cache; source line and numeric command expansion changes must be reflected here.

Risks and test signals: validates command range expansion, local-return facts, helper call propagation, and large constant handling.
