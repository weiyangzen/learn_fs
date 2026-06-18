# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/ioctl.h

Purpose: this fixture recreates the basic Linux ioctl encoding macros used by ioctl extraction tests.

Important APIs and flow: it defines direction constants, bit widths, shifts, `_IOC`, and convenience macros `_IO`, `_IOR`, `_IOW`, and `_IOWR`. `_IOC` composes direction, type, number, and size into a command integer.

State and persistence: preprocessor constants only.

Dependencies and integration: included by file-operation UAPI fixtures and unused ioctl fixtures. Numeric ioctl values generated from these macros appear in JSON constants and command scopes.

Risks: this is a simplified architecture-independent copy; real kernel ioctl definitions may vary by arch or include extra helper macros.

Test signals: validates that clang constant extraction and declextract's ioctl decoder can interpret macro-generated command values.
