# sources/test-tools/strace/bundled/linux/include/uapi/linux/perf_event.h

## Purpose

Defines the public ABI for `perf_event_open(2)`, perf event file descriptor ioctls, mmap metadata pages, perf ring-buffer records, sampling format flags, branch records, and data-source encodings. In strace this header is the basis for decoding `perf_event_attr`, `PERF_EVENT_IOC_*`, and perf-related flags passed through syscalls and ioctls.

## Important APIs, Types, and Dependencies

Dependencies are `linux/types.h`, `linux/ioctl.h`, and `asm/byteorder.h`. The large exported surface includes event families (`perf_type_id`), hardware/software/cache event ids, `perf_event_sample_format`, branch sampling flags and branch classifications, register ABI ids, transaction bits, `perf_event_read_format`, and the versioned `PERF_ATTR_SIZE_VER*` constants. `struct perf_event_attr` is the primary syscall input and contains type/config selectors, sampling period/frequency unions, sample/read format masks, many one-bit behavior flags, breakpoint/probe/config extension unions, register masks, AUX options, signal data, and newer `config3`/`config4` extensions. `struct perf_event_query_bpf` and `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `REFRESH`, `RESET`, `PERIOD`, `SET_OUTPUT`, `SET_FILTER`, `ID`, `SET_BPF`, `PAUSE_OUTPUT`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES` define fd ioctl interactions. `struct perf_event_mmap_page` defines seqlock-protected counter/time metadata plus data and AUX ring offsets. Record ABI exports include `struct perf_event_header`, namespace link info, `enum perf_event_type` through `PERF_RECORD_CALLCHAIN_DEFERRED`, ksymbol and BPF event types, callchain context markers, AUX flags, syscall flags `PERF_FLAG_FD_*`, `union perf_mem_data_src`, memory hierarchy macros, `struct perf_branch_entry`, and `union perf_sample_weight`.

## Control Flow, State, and Integration

The header is declarative, but it documents several ABI control flows: opening an event with `perf_event_attr`, controlling it through fd ioctls, reading counts through `read()` according to `read_format`, mapping a metadata page and ring buffer, using seqlock loops for self-monitoring reads, and parsing variable-length records according to `perf_event_header.size` and selected sample bits. Persistent state lives in kernel perf events, attached BPF programs, mmap data/AUX rings, group relationships, and per-task/per-cpu counters.

## Risks and Test Signals

Risks are high because the ABI is densely versioned and bitfield-heavy. Decoders must honor `attr.size`, endian-specific bitfield layouts, reusable `PERF_RECORD_MISC_*` bits whose meaning depends on record type, variable payload order under `sample_type`, and ring-buffer memory barriers described by the header. Test signals include strace coverage for `perf_event_open` with old and new attr sizes, every known `PERF_EVENT_IOC_*`, grouped read formats, `PERF_FLAG_FD_CLOEXEC`, BPF query payloads, and unknown future record/sample bits printed without corrupting following fields.
