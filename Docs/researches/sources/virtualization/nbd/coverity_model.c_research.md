# File Research: sources/virtualization/nbd/coverity_model.c

Small Coverity model file for GLib array append behavior.

It forward-declares `GArray`, maps `g_array_append_val(a, v)` to `g_array_append_vals(a, &(v), 1)`, and defines `g_array_append_vals()` to call `__coverity_escape__`.

This is analysis-only modeling, not production implementation.
