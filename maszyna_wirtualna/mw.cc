/*
 * Kod interpretera maszyny rejestrowej do projektu z JFTT2023
 *
 * Autor: Maciek Gębala
 * http://ki.pwr.edu.pl/gebala/
 * 2023-11-15
 * (wersja long long)
 */
#include <iostream>
#include <locale>

#include <utility>
#include <vector>
#include <map>

#include <cstdlib> // rand()
#include <ctime>

#include "instructions.hh"
#include "colors.hh"

using namespace std;

void run_machine(vector<pair<int, int>> &program)
{
  map<long long, long long> pam;

  long long r[8], tmp;
  long long lr;

  long long t, io;

  cout << cBlue << "Uruchamianie programu." << cReset << endl;
  lr = 0;
  srand(time(NULL));
  for (int i = 0; i < 8; i++)
    r[i] = rand();
  t = 0;
  io = 0;
  while (program[lr].first != HALT) // HALT
  {
    cout << cCyan << lr << " ||\t";
    for (int i = 0; i < 8; i++)
      cout << r[i] << "\t";
    cout << " || " << t << "\t";
    cout << io << cReset << endl;

    cout
        << cMagenta << "Zawartość pamięci: ";
    map<long long, long long>::iterator memoryIt = pam.begin();
    while (memoryIt != pam.end())
    {
      cout
          << "[" << memoryIt->first << "] = " << memoryIt->second << "\t";
      memoryIt++;
    }
    cout << cReset
         << endl;

    switch (program[lr].first)
    {
    case READ:
      cout << "? ";
      cin >> r[0];
      io += 100;
      lr++;
      break;
    case WRITE:
      cout << "> " << r[0] << endl;
      io += 100;
      lr++;
      break;

    case LOAD:
      r[0] = pam[r[program[lr].second]];
      t += 50;
      lr++;
      break;
    case STORE:
      pam[r[program[lr].second]] = r[0];
      t += 50;
      lr++;
      break;

    case ADD:
      r[0] += r[program[lr].second];
      t += 5;
      lr++;
      break;
    case SUB:
      r[0] -= r[0] >= r[program[lr].second] ? r[program[lr].second] : r[0];
      t += 5;
      lr++;
      break;
    case GET:
      r[0] = r[program[lr].second];
      t += 1;
      lr++;
      break;
    case PUT:
      r[program[lr].second] = r[0];
      t += 1;
      lr++;
      break;
    case RST:
      r[program[lr].second] = 0;
      t += 1;
      lr++;
      break;
    case INC:
      r[program[lr].second]++;
      t += 1;
      lr++;
      break;
    case DEC:
      if (r[program[lr].second] > 0)
        r[program[lr].second]--;
      t += 1;
      lr++;
      break;
    case SHL:
      r[program[lr].second] <<= 1;
      t += 1;
      lr++;
      break;
    case SHR:
      r[program[lr].second] >>= 1;
      t += 1;
      lr++;
      break;

    case JUMP:
      lr = program[lr].second;
      t += 1;
      break;
    case JPOS:
      if (r[0] > 0)
        lr = program[lr].second;
      else
        lr++;
      t += 1;
      break;
    case JZERO:
      if (r[0] == 0)
        lr = program[lr].second;
      else
        lr++;
      t += 1;
      break;

    case STRK:
      r[program[lr].second] = lr;
      t += 1;
      lr++;
      break;
    case JUMPR:
      lr = r[program[lr].second];
      t += 1;
      break;

    default:
      break;
    }

    if (lr < 0 || lr >= (int)program.size())
    {
      cerr << cRed << "Błąd: Wywołanie nieistniejącej instrukcji nr " << lr << "." << cReset << endl;
      exit(-1);
    }
  }
  cout.imbue(std::locale(""));
  cout << cBlue << "Skończono program (koszt: " << cRed << (t + io) << cBlue << "; w tym i/o: " << io << ")." << cReset << endl;
}
