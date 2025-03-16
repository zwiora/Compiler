/*
 * Instrukcje maszyny wirtualnej do projektu z JFTT2023
 *
 * Autor: Maciek Gębala
 * http://ki.pwr.edu.pl/gebala/
 * 2023-11-15
*/
#pragma once

enum Instructions : int { READ, WRITE, LOAD, STORE, ADD, SUB, GET, PUT, RST, INC, DEC, SHL, SHR, JUMP, JPOS, JZERO, STRK, JUMPR, HALT };
