# File Research: sources/teaching/minix/minix/drivers/storage/floppy/floppy.c

## Purpose

Implements the user-space MINIX floppy disk controller driver for PC NEC PD765-compatible FDC hardware, including disk density probing, DMA setup, sector I/O, formatting support, partition handling, motor timers, interrupts, retries, resets, and SEF startup.

## Main Entry Points

- `main()`: starts SEF and enters `blockdriver_task()`.
- `sef_cb_init_fresh()`: allocates the DMA buffer, initializes per-drive state/timers, registers the floppy IRQ, and announces the block driver.
- `f_transfer()`: central block transfer path for reads, writes, and format devices.
- `f_do_open()` / `f_do_close()`: open/close handling and automatic density detection.
- `f_prepare()` / `f_part()` / `f_geometry()`: minor-device selection, partition lookup, and geometry reporting.
- `dma_setup()`: programs the ISA DMA controller for a one-sector transfer.
- `start_motor()` / `stop_motor()`: manage drive motor state and delayed spin-down.
- `seek()`, `recalibrate()`, `f_reset()`: position and recover the FDC.
- `fdc_transfer()`, `fdc_command()`, `fdc_out()`, `fdc_results()`, `f_intr_wait()`: low-level command, interrupt, and status handling.
- `test_read()`: probes media/drive density combinations.

## Control Flow And State

The driver keeps one `struct floppy` per drive with current cylinder, target CHS, density, class mask, geometry, partitions, and motor timer. Global state tracks the selected drive/device, density parameters, controller reset need, current motor bitmap, busy state, and FDC result bytes.

`f_transfer()` validates sector alignment and EOF, truncates to device size, maps iovecs to track sectors, starts the motor, configures FDC timing/rate, seeks, and transfers one sector at a time through the DMA buffer. On errors it retries up to `MAX_ERRORS`, recalibrating halfway, and stops immediately for nonretryable errors such as write protection. Formatting uses a special minor bit and consumes `struct disk_parameter_s` from the request.

Open on typed devices selects density directly. Open on `/dev/fdN` probes density through `test_order`, reading a diagnostic sector and then parsing partitions on success. Cleanup schedules a motor-off timer after each request.

Interrupt waits use `driver_receive()` and local timer expiration to distinguish real hardware interrupt from timeout. FDC status reads reenable IRQs after consuming result bytes. Reset strobes DOR, flushes sense results for all four possible drives, and marks all configured drives uncalibrated.

## Dependencies

Depends on MINIX blockdriver/drvlib/syslib/sysutil APIs, timers, safe copy grants, PC port I/O, IRQ policy calls, ISA DMA registers, `machine/diskparm.h`, and live update callbacks supplied by `liveupdate.c`.

## Risks

This is hardware-state-heavy code. Risks include ISA DMA address restrictions below 16 MB, timing-sensitive motor/seek/FDC operations, controller reset sequencing, lost or spurious interrupts, density misdetection, and retry behavior that mutates iovecs in place. The format-device path trusts controller validation for most formatting parameters after only checking sector count. Live update and termination must avoid stopping while `f_busy` indicates active I/O.
