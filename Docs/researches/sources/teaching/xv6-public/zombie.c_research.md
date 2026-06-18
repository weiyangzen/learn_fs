# File Research: sources/teaching/xv6-public/zombie.c

Small user program that creates a zombie process.

Behavior:
- Parent sleeps briefly after fork.
- Child exits immediately.
- Parent then exits.

Purpose:
- Demonstrates zombie/reparenting behavior under `init`.
