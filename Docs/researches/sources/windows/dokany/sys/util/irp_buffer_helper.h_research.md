# File Research: sources/windows/dokany/sys/util/irp_buffer_helper.h

Header and macro layer for safe Dokan IRP buffer extraction, validation, and output construction.

Key responsibilities:
- Declares input-buffer helpers `GetProvidedInputSize` and `GetInputBuffer`.
- Defines generic input buffer validation macros with configurable exit behavior.
- Defines size-comparison macros for fixed structs and variable-sized structs such as `MOUNTDEV_NAME`, `DOKAN_NOTIFY_PATH_INTERMEDIATE`, and `DOKAN_UNICODE_STRING_INTERMEDIATE`.
- Provides `GET_IRP_BUFFER*` macro variants that return, break, leave, or no-op on failure.
- Declares output helpers for fixed reservation, incremental extension, and variable-length string append.
- Provides `PREPARE_OUTPUT`, a typed convenience macro around `PrepareOutputWithSize`.

Important behavior:
- The input macros fetch the actual buffer through `GetInputBuffer`, assert it is non-null, validate that the provided size fits the expected structure, log invalid sizes, and invoke the selected exit macro.
- Variable-sized input checks validate both fixed header size and embedded length fields against the provided buffer length.
- `DOKAN_UNICODE_STRING_INTERMEDIATE_SIZE_COMPARE` additionally rejects `Length > MaximumLength`.
- The output helper comments define the `IoStatus.Information` convention used by the implementation.

Dependencies:
- Includes `<ntifs.h>` and `../public.h`.
- Used broadly by Dokan dispatch files such as access, device, event, fscontrol, notification, timeout, volume, and fileinfo handlers.

Notable risks:
- The macros assume local variables such as `status` exist for `DOKAN_EXIT_LEAVE` and `DOKAN_EXIT_BREAK`.
- Macro arguments are evaluated in generated blocks and should be simple lvalues.
- The header guard name is `STRUCT_HELPER_H_`, which does not match the filename but is functionally unique in this file.
