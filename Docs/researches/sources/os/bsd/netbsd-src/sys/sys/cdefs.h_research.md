# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs.h

## Scope

Core NetBSD C portability and compiler-definition header.

## APIs And Behavior

- Provides compiler feature tests `__GNUC_PREREQ__`, `__has_feature`, and `__has_extension`.
- Includes machine cdefs and object-format-specific cdefs for ELF or a.out.
- Defines concatenation/stringification, K&R/ANSI prototype support, reserved keyword compatibility, compile-time assertions, const/volatile/function pointer cast helpers, and `__extension__` fallback.
- Defines attributes for noreturn, pure, const, noinline, always_inline, sentinel, returns_twice, noclone, unused, used, diagnostic/debug usage, no profiling, unreachable, sanitizer suppression, packed/aligned/section, visibility, C++ extern blocks, C99 inline, restrict, and function name fallback.
- Defines symbol renaming outside kernel/standalone builds.
- Provides instruction barrier and branch prediction macros.
- Defines printf/scanf/syslog format attributes and format_arg.
- Provides link set iteration and entry helpers.
- Defines alignment, array count, bit/mask/range helpers, shift-in/out helpers, C/C++ cast helpers, unused-expression helpers, and integer type fit/min/max macros.

## Dependencies

- Pulls in machine and object-format cdefs; relies on compiler predefined integer and char-bit types.

## Risks And Invariants

- This header underpins most other headers; macro compatibility with C, C++, assembler, lint, GCC, Clang, and PCC matters.
- Object-format-specific includes must define aliases, identifiers, and link set primitives expected here.
- Bit/type macros can evaluate arguments in compile-time contexts and must avoid unintended side effects where documented.
