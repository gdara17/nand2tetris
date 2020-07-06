// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    @R1
    D=M //D = R1
    @i
    M=D //i = R1
    
    @product
    M=0 //product = 0

(LOOP)
    @i
    D=M //D = R1
    @STOP 
    D;JEQ //if (i == 0) jump to STOP
    
    @R0
    D=M //D = R0
    @product
    M=D+M //product += R0

    @i
    M=M-1 //i--
    
    @LOOP
    0;JMP

(STOP)
    @product
    D=M

    @R2
    M=D //R2 = product

(END)
    @END
    0;JMP