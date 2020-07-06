// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_1
D;JNE
@SP
A=M-1
M=-1
@CONTINUE_1
0;JMP
(FALSE_1)
@SP
A=M-1
M=0
(CONTINUE_1)
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_2
D;JNE
@SP
A=M-1
M=-1
@CONTINUE_2
0;JMP
(FALSE_2)
@SP
A=M-1
M=0
(CONTINUE_2)
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_3
D;JNE
@SP
A=M-1
M=-1
@CONTINUE_3
0;JMP
(FALSE_3)
@SP
A=M-1
M=0
(CONTINUE_3)
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_4
D;JGE
@SP
A=M-1
M=-1
@CONTINUE_4
0;JMP
(FALSE_4)
@SP
A=M-1
M=0
(CONTINUE_4)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_5
D;JGE
@SP
A=M-1
M=-1
@CONTINUE_5
0;JMP
(FALSE_5)
@SP
A=M-1
M=0
(CONTINUE_5)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_6
D;JGE
@SP
A=M-1
M=-1
@CONTINUE_6
0;JMP
(FALSE_6)
@SP
A=M-1
M=0
(CONTINUE_6)
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_7
D;JLE
@SP
A=M-1
M=-1
@CONTINUE_7
0;JMP
(FALSE_7)
@SP
A=M-1
M=0
(CONTINUE_7)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_8
D;JLE
@SP
A=M-1
M=-1
@CONTINUE_8
0;JMP
(FALSE_8)
@SP
A=M-1
M=0
(CONTINUE_8)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@FALSE_9
D;JLE
@SP
A=M-1
M=-1
@CONTINUE_9
0;JMP
(FALSE_9)
@SP
A=M-1
M=0
(CONTINUE_9)
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// neg
@SP
A=M-1
D=0
M=D-M
// and
@SP
AM=M-1
D=M
A=A-1
M=M&D
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
A=A-1
M=M|D
// not
@SP
A=M-1
M=!M
