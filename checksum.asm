ld r3 r0 8
sub r4 r4
sll r3 r4 0 12
st r0 r3 8
add r1 r0 0
add r2 r0 0
add r6 r0 5
ld r3 r2 0
slr r4 r3 16 0
sub r5 r5
sll r5 r3 0 12
add r1 r4 0
add r1 r5 0
add r2 r0 4
sub r6 r0 1
jnz pc -36
slr r4 r1 16 0
sub r5 r5
sll r5 r1 0 12
sub r1 r1
add r1 r4 0
add r1 r5 0
slr r4 r1 16 0
sub r5 r5
sll r5 r1 0 12
sub r1 r1
add r1 r4 0
add r1 r5 0
neg r1 r1
ld r3 r0 8
sll r3 r1 0 12
st r0 r3 8
halt
