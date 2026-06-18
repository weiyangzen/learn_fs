# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/logindmux.h

## Role

Public ioctl/data header for logindmux, the STREAMS module that exchanges queue pairs between a pty master stream and a network stream.

## Structure

Defines `struct protocol_arg`, `_SYSCALL32` `protocol_arg32`, telnet magic cookie `M_CTL_MAGIC_NUMBER`, `TELIOC` base if not already defined, and `LOGDMX_IOC_QEXCHANGE`.

## Dependencies And Consumers

Uses device typedefs from including context. User/kernel ioctl paths use the protocol argument structures; STREAMS logindmux implementation uses the ioctl constant.

## Important Details

The ioctl base comment carries an old "fixme" note. The 32-bit structure preserves device and flag width for LP64 kernel compatibility.

## Research Notes

Read completely: 64 lines, 1528 bytes.
