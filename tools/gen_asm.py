#!/usr/bin/env python3
"""Writes the SHA-NI block loop of sha2/sha256.ri: RustCrypto sha2 0.10.9's
src/sha256/x86.rs, `digest_blocks`, one intrinsic per instruction.

Registers: rdi state, r9 data, r10 blocks left, rcx K, r8 byte-swap mask;
xmm0 the message plus K, xmm1 ABEF, xmm2 CDGH, xmm3-xmm7 w0-w4, xmm8 the
mask, xmm9/xmm10 the saved state, xmm11/xmm12 scratch."""

W = ["%xmm3", "%xmm4", "%xmm5", "%xmm6", "%xmm7"]
out = []
emit = out.append

def rounds4(rest, i):
    emit(f"movdqa {rest}, %xmm0")
    emit(f"paddd {16 * i}(%rcx), %xmm0")
    emit("sha256rnds2 %xmm0, %xmm1, %xmm2")
    emit("pshufd $$0x0E, %xmm0, %xmm0")
    emit("sha256rnds2 %xmm0, %xmm2, %xmm1")

def schedule(v0, v1, v2, v3, dst):
    emit(f"movdqa {v0}, %xmm11")
    emit(f"sha256msg1 {v1}, %xmm11")
    emit(f"movdqa {v3}, %xmm12")
    emit(f"palignr $$4, {v2}, %xmm12")
    emit("paddd %xmm12, %xmm11")
    emit(f"sha256msg2 {v3}, %xmm11")
    emit(f"movdqa %xmm11, {dst}")

emit("movq %rsi, %r9")
emit("movq %rdx, %r10")
emit("movdqu (%r8), %xmm8")
emit("movdqu (%rdi), %xmm1")
emit("movdqu 16(%rdi), %xmm2")
emit("pshufd $$0xB1, %xmm1, %xmm1")
emit("pshufd $$0x1B, %xmm2, %xmm2")
emit("movdqa %xmm1, %xmm11")
emit("palignr $$8, %xmm2, %xmm11")
emit("pblendw $$0xF0, %xmm1, %xmm2")
emit("movdqa %xmm11, %xmm1")
emit("1:")
emit("movdqa %xmm1, %xmm9")
emit("movdqa %xmm2, %xmm10")
for i in range(4):
    emit(f"movdqu {16 * i}(%r9), {W[i]}")
    emit(f"pshufb %xmm8, {W[i]}")
for i in range(4):
    rounds4(W[i], i)
for i in range(4, 16):
    j = i - 4
    v = [W[(j + k) % 5] for k in range(5)]
    schedule(v[0], v[1], v[2], v[3], v[4])
    rounds4(v[4], i)
emit("paddd %xmm9, %xmm1")
emit("paddd %xmm10, %xmm2")
emit("addq $$64, %r9")
emit("decq %r10")
emit("jnz 1b")
emit("pshufd $$0x1B, %xmm1, %xmm1")
emit("pshufd $$0xB1, %xmm2, %xmm2")
emit("movdqa %xmm1, %xmm11")
emit("pblendw $$0xF0, %xmm2, %xmm11")
emit("palignr $$8, %xmm1, %xmm2")
emit("movdqu %xmm11, (%rdi)")
emit("movdqu %xmm2, 16(%rdi)")

pad = " " * 10
print("asm(\"" + ("\n" + pad + " ").join(out) + "\"")
