# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-stdout.c

This file implements human-readable stdout output for LM plugin data structures.

Behavior:
- `stdout_controller_state_data()` decodes a full `nvme_lm_controller_state_data` buffer.
- It prints the outer controller-state header, including version, attributes, NVMe controller state size, and vendor-specific size.
- It prints the nested NVMe controller state header and then iterates submission and completion queue records.
- With verbose flags, it decodes selected bitfields for suspended state, submission queue priority/contiguity, completion queue interrupt/phase/contiguity fields.
- It detects and warns about truncated headers or truncated queue arrays based on the supplied buffer length.
- `stdout_show_controller_data_queue()` prints CDQ head pointer and tail pointer trigger.
- `lm_get_stdout_print_ops()` stores flags and returns the stdout ops table.

Notable quirk:
- The completion-queue pointer is calculated as `&data->data.cqs[niosq + i]`; given typical flexible layout naming, this may intentionally account for submission queue storage preceding completions, but it is worth checking against the exact struct definition in libnvme headers.
