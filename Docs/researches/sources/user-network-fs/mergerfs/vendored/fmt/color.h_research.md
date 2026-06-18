# sources/user-network-fs/mergerfs/vendored/fmt/color.h

## Purpose

This fmt header adds ANSI color and emphasis styling support. It defines named RGB colors, terminal color codes, text emphasis flags, a compact `text_style` representation, and formatting/printing helpers that wrap normal fmt output in ANSI escape sequences.

## Important APIs, types, and functions

Public types include `enum class color`, `enum class terminal_color`, `enum class emphasis`, `struct rgb`, and `class text_style`. Public helpers include `fg`, `bg`, `operator|` for styles/emphasis, styled overloads of `print`, `format`, `format_to`, and `vformat_to`, plus `styled(value, text_style)`.

Internal `detail::color_type` stores either unset, RGB, or terminal color state. `detail::ansi_color_escape<Char>` builds escape sequences for truecolor foreground/background, terminal colors, and emphasis combinations. `detail::styled_arg<T>` is a view wrapper with a formatter specialization that applies style only around a single argument.

## Control Flow

`text_style` bit-packs foreground, background, and emphasis into a 64-bit integer. `operator|=` checks for invalid OR combinations involving terminal colors by adding style words and testing overflow bits in the color discriminator regions, then merges with bitwise OR.

Formatting flow emits emphasis, foreground, and background escapes if present, delegates to normal `vformat_to` or an underlying `formatter<T>`, and appends `ESC[0m` when a style was applied. Terminal colors use SGR color codes; RGB colors use `38;2;r;g;b` or `48;2;r;g;b` sequences.

## State and Persistence Behavior

Styles are value objects. Formatting allocates temporary buffers for string-returning and file-printing overloads but does not persist global style state. The terminal state is reset after styled output when a non-empty style is used.

## Dependencies and Integration Points

It includes `format.h` and uses fmt buffers, `format_args`, `buffered_context`, `formatter`, `copy`, `print`, and `to_string`. It integrates with terminals that understand ANSI SGR escape sequences and with fmt's normal compile-time checked formatting APIs.

## Risks and Edge Cases

ANSI support is terminal-dependent; redirected output will contain raw escape bytes. OR-ing terminal colors with existing colors is rejected, but RGB foreground and background combinations are allowed. Emphasis constructor output assumes at least one emphasis bit when used through `has_emphasis`. Wide-character output uses templated `Char` escapes but actual terminal interpretation may still be byte-oriented. Resetting with `ESC[0m` clears all styles, not only those introduced by this call.

## Test Signals

Tests should verify exact escape sequences for RGB foreground/background, terminal colors, each emphasis bit, combined styles, reset emission, invalid terminal color OR errors, styled single-argument formatting, `format`, `format_to`, `print(FILE*)`, and behavior with empty/default `text_style`.
