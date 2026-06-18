# File Research: sources/os/linux/linux/mm/kmsan/kmsan.h

## Role

Private KMSAN runtime header. It defines runtime constants, metadata pointer structures, bug reasons, context helpers, recursion guards, origin extra-bit encoding, internal function prototypes, and address classification helpers.

## Key Definitions

- Magic origin markers:
  - `KMSAN_ALLOCA_MAGIC_ORIGIN`
  - `KMSAN_CHAIN_MAGIC_ORIGIN`
- Poison flags:
  - `KMSAN_POISON_NOCHECK`
  - `KMSAN_POISON_CHECK`
  - `KMSAN_POISON_FREE`
- Metadata constants:
  - `KMSAN_ORIGIN_SIZE` is 4 bytes.
  - `KMSAN_MAX_ORIGIN_DEPTH` is 7.
  - `KMSAN_STACK_DEPTH` is 64.
  - `KMSAN_META_SHADOW` and `KMSAN_META_ORIGIN` select metadata type.
- `struct shadow_origin_ptr` packages shadow and origin pointers for compiler hooks.
- `enum kmsan_bug_reason` distinguishes generic uninitialized use, copy-to-user leaks, and USB submit leaks.

## Runtime Context

- Declares per-CPU KMSAN context for interrupt contexts.
- `kmsan_get_context()` returns `current->kmsan_ctx` in task context or the raw per-CPU context otherwise.
- `kmsan_in_runtime()` suppresses recursive runtime entry and conservatively treats nested hard IRQs and NMIs as runtime.
- `kmsan_enter_runtime()` and `kmsan_leave_runtime()` increment/decrement per-context runtime nesting with warnings on unexpected nesting.

## Origin Extra Bits

- `kmsan_extra_bits()` packs origin chain depth and use-after-free state into stack-depot extra bits.
- `kmsan_uaf_from_eb()` and `kmsan_depth_from_eb()` unpack those fields.

## Internal API

Declares internal routines for:

- Metadata copying, poisoning, unpoisoning, and setting shadow/origin.
- Origin chaining and stack saving.
- Task-context creation.
- Memory checking and reporting.
- Metadata contiguity checks.
- Vmalloc metadata page lookup.
- Page metadata setup.
- Early range metadata allocation.

## Address Helpers

- `kmsan_internal_is_module_addr()` checks module virtual address range.
- `kmsan_internal_is_vmalloc_addr()` checks vmalloc virtual address range.
- These are simple non-instrumented replacements for helpers that might recurse inside KMSAN runtime.

## Research Notes

This header is the coupling point for KMSAN runtime files. The inline runtime guard and context selection logic are particularly important because nearly every KMSAN hook depends on avoiding recursive sanitizer execution.
