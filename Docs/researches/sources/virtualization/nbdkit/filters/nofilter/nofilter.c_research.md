# File Research: sources/virtualization/nbdkit/filters/nofilter/nofilter.c

This file registers an nbdkit filter named `nofilter` with only `.name` and `.longname` set. It implements no callbacks, so nbdkit's normal filter passthrough behavior applies to all capabilities and requests.

The file is useful as a minimal filter skeleton or behavior-control placeholder. It carries no state, no configuration, and no direct operational risk beyond adding an extra module layer.
