# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf_impl.h

Private implementation header for the Device Autoconfiguration Framework. It defines DACF module/rule/argument/reservation state, hash sizes, parsing helpers, rule matching/reference management, reservation processing, operation invocation, debugging flags, and DDI hook entry points.

Key elements:
- `dacf_module_t` tracks a DACF module name, lock, loaded state, and opset table.
- Defines small hash-table sizes for rules, modules, and info handles.
- Reservation-processing flags distinguish invoke and release passes.
- Device specifier enum supports matching by minor node type, driver minor name, or device path.
- `dacf_arg_t` is a linked list of named operation arguments.
- `dacf_rule_t` stores match data, module/opset/opid target, options, reference count, and operation arguments.
- `dacf_rsrvlist_t` records reserved rules to invoke later, their info handle, last result, and next pointer.
- Kernel-only declarations cover global DACF lock, module register/unregister, argument insertion/deletion, initialization, binding-file reading, rule clearing, string-to-enum parsing, option parsing, rule insertion/hold/release, reservation creation/processing/clearing, rule matching, and operation invocation.
- Defines detailed invocation failure codes for missing module, missing opset, missing op, and failed op.
- Debug flags distinguish generic messages and devinfo diagnostics.
- DACF client support hooks match minor creation and invoke post-attach/pre-detach processing.

Dependencies:
- Includes public `dacf.h`; relies on kernel locks, DDI minor data, devinfo nodes, and configuration-file parsing implemented elsewhere.
- Tied to DDI attach/detach and minor-node creation hooks.

Research notes:
- Rules are reference-counted and may be reserved for delayed processing, so attach/detach paths must handle lifetimes across module loading and invocation.
- Matching is data-driven from DACF binding files and can target different device identifiers.
