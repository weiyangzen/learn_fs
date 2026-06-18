# sources/user-network-fs/samba/source4/param/tests/loadparm.c

Purpose: `param/tests/loadparm.c` defines local torture tests for loadparm context creation, option parsing, parametric options, service lookup, and server role derivation.

Important APIs, types, and functions: It contains test functions for `loadparm_init`, `lpcfg_set_option`, `lpcfg_set_cmdline`, `lpcfg_do_global_parameter`, `lpcfg_do_global_parameter_var`, parametric double/bool/int/bytes accessors, service parameter setting, service lookup, and server role/security combinations. `torture_local_loadparm` registers the suite.

Control flow: Each test creates a fresh loadparm context, applies one or more configuration changes, then asserts getter results. Server role tests cover standalone, AD DC, member, PDC/BDC inference, and security-driven member inference.

State and persistence behavior: Tests use in-memory loadparm contexts only; no config files are written. They validate state transitions inside the context.

Dependencies and integration points: It depends on Samba torture framework, loadparm APIs, share declarations, and server role constants.

Risks: Coverage is focused on core parsing and role inference, not Python bindings or file loading. It assumes default role/security values that can change with global defaults.

Test signals: This file is itself a signal for `param/loadparm` behavior. New option parsing logic should add simple tests here for invalid syntax, defaults, and parametric value conversion.
