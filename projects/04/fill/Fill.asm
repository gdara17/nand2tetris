// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(KEYBOARDLOOP)
    @KBD
    D=M
    @DISPLAYBLACK
    D;JNE
    @DISPLAYWHITE
    D;JEQ
    @KEYBOARDLOOP
    0;JMP

(DISPLAYBLACK)
    @SCREEN
    D=A
    @addr
    M=D //addr = screen's base

    @numprocessed //number of groups (16 pixels) processed
    M=0
(DISPLAYBLACKLOOP)
    @numprocessed
    D=M //D = numprocessed
    @8192
    D=A-D //D = numleft
    @KEYBOARDLOOP
    D;JEQ //if (numleft == 0) jump to KEYBOARDLOOP

    @addr
    A=M
    M=-1 // RAM[addr] = 1111111111111111

    @numprocessed
    M=M+1 //numprocessed++
    @addr
    M=M+1 //addr++

    @DISPLAYBLACKLOOP
    0;JMP


(DISPLAYWHITE)
    @SCREEN
    D=A
    @addr
    M=D //addr = screen's base

    @numprocessed //number of groups (16 pixels) processed
    M=0
(DISPLAYWHITELOOP)
    @numprocessed
    D=M //D = numprocessed
    @8192
    D=A-D //D = numleft
    @KEYBOARDLOOP
    D;JEQ //if (numleft == 0) jump to KEYBOARDLOOP

    @addr
    A=M
    M=0 // RAM[addr] = 0000000000000000

    @numprocessed
    M=M+1 //numprocessed++
    @addr
    M=M+1 //addr++

    @DISPLAYWHITELOOP
    0;JMP

    

